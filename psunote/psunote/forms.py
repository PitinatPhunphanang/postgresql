from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets
import models

class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        data = []
        if valuelist:
            # แยกค่าของแท็กด้วยจุลภาคแล้วเก็บในลิสต์
            data = [x.strip() for x in valuelist[0].split(",")]

        if not self.remove_duplicates:
            self.data = data
            return

        # ลบแท็กที่ซ้ำกัน
        self.data = []
        for d in data:
            if d not in self.data:
                self.data.append(d)

    def _value(self):
        # คืนค่าเป็นสตริงที่แยกแท็กด้วยจุลภาค
        if self.data:
            return ", ".join([tag.name if isinstance(tag, models.Tag) else tag for tag in self.data])
        else:
            return ""

# สร้างฟอร์มจากโมเดล Note โดยใช้ FlaskForm
BaseNoteForm = model_form(
    models.Note, base_class=FlaskForm, exclude=["created_date", "updated_date"], db_session=True
)

class NoteForm(BaseNoteForm):
    # ฟิลด์แท็กใช้ TagListField ที่กำหนดเอง
    tags = TagListField("Tag")
