import flask
import models
import forms

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)

@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )

@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []  # ล้างแท็กเดิมทั้งหมดก่อน

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )
        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)
        note.tags.append(tag)  # เพิ่มแท็กใหม่เข้าไป

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))

@app.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
def notes_edit(note_id):
    db = models.db
    note = db.session.get(models.Note, note_id)

    if not note:
        flask.abort(404, description="ไม่พบโน้ตที่ระบุ")

    form = forms.NoteForm(obj=note)

    if form.validate_on_submit():
        # อัปเดตเฉพาะฟิลด์ title และ description
        note.title = form.title.data
        note.description = form.description.data
        
        # ล้างแท็กเดิมทั้งหมดก่อน
        note.tags = []

        # จัดการแท็กใหม่ทีละตัว
        for tag_name in form.tags.data:
            tag = (
                db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
                .scalars()
                .first()
            )
            if not tag:
                # ถ้าไม่มีแท็กนี้ในฐานข้อมูลก็สร้างใหม่
                tag = models.Tag(name=tag_name)
                db.session.add(tag)

            note.tags.append(tag)  # เพิ่มแท็กใหม่เข้าไปในโน้ต

        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("notes-edit.html", form=form, note=note)

@app.route("/notes/delete/<int:note_id>", methods=["POST"])
def notes_delete(note_id):
    db = models.db
    note = db.session.get(models.Note, note_id)

    if not note:
        flask.abort(404, description="ไม่พบโน้ตที่ระบุ")

    # ลบโน้ตจากฐานข้อมูล
    db.session.delete(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/notes/delete-tag/<int:note_id>/<string:tag_name>", methods=["POST"])
def notes_delete_tag(note_id, tag_name):
    db = models.db
    note = db.session.get(models.Note, note_id)

    if not note:
        flask.abort(404, description="ไม่พบโน้ตที่ระบุ")

    # ค้นหาแท็กตามชื่อที่ได้รับมา
    tag = db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name)).scalars().first()

    if tag in note.tags:
        # ถ้ามีแท็กนี้ในโน้ต ให้ลบออก
        note.tags.remove(tag)
        db.session.commit()

    return flask.redirect(flask.url_for("index"))



@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )

if __name__ == "__main__":
    app.run(debug=True)
