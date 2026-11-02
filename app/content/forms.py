from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class AnnouncementForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    body = TextAreaField("Message", validators=[DataRequired()])

    is_published = BooleanField("Publish immediately", default=True)

    expires_date = DateField(
        "Expires On (Optional)",
        validators=[Optional()],
    )

    submit = SubmitField("Save Announcement")

class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired(), Length(max=200)])
    body = TextAreaField("Description", validators=[DataRequired()])
    
    event_date = DateField("Event Date", validators=[DataRequired()])
    event_time = StringField("Event Time (e.g. 6:00 PM)", validators=[Optional(), Length(max=40)])
    location = StringField("Location", validators=[Optional(), Length(max=200)])
    
    image = FileField(
        "Event Flyer / Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only (jpg, png, gif)"),
        ],
    )
    
    is_published = BooleanField("Publish immediately", default=True)
    expires_date = DateField("Expires On (Optional)", validators=[Optional()])
    
    submit = SubmitField("Save Event")    


class SermonForm(FlaskForm):
    title = StringField("Sermon Title", validators=[DataRequired(), Length(max=200)])
    speaker = StringField("Speaker", validators=[DataRequired(), Length(max=120)])
    body = TextAreaField("Description / Series Notes", validators=[Optional()])
    event_date = DateField("Sermon Date", validators=[DataRequired()])
    video_url = StringField("Video URL (YouTube Link)", validators=[Optional(), Length(max=500)])
    
    submit = SubmitField("Save Sermon")


class ServiceTimeForm(FlaskForm):
    service_name = StringField("Service Name", validators=[DataRequired(), Length(max=80)])
    day_of_week = StringField("Day of Week (e.g. Sunday)", validators=[DataRequired(), Length(max=20)])
    start_time = StringField("Start Time (e.g. 7:00 AM)", validators=[DataRequired(), Length(max=20)])
    end_time = StringField("End Time (e.g. 9:30 AM)", validators=[Optional(), Length(max=20)])
    
    submit = SubmitField("Save Service Time")    