## Moodle Events Notifier

#### Web Scrap (with selenium) Moodle events needed to be complete and sync them to Google Keep to track your homework progress and never forget about applying tasks on time.
#### Manage all configurations with simple CLI tool (click library).

#### Dependencies:
- Selenium Chrome Web driver
- Redis Database
- Click (CLI Tool)

### Usage:
```
from moodle_manager import MoodleManager

moodle = MoodleManager()
moodle.get_events(username='', password='')

moodle.insert_event_calendar(schedule=True)
moodle.insert_event_keep(schedule=True)

moodle.send_email_report(emails=['my_email@email.com'], weekly_report=False)
```

### CLI tool functionality:
```
 >py cli.py
    Usage: cli.py [OPTIONS] COMMAND [ARGS]...
    
      CLI tool for managing Moodle Events Notifier
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      add_email     Add email address to scheduled report
      insert_event  Insert event to Google Keep (list) \ Calendar
      remove_email  Remove email address from scheduled report
      show_emails   List all names and email addresses of scheduled report
      show_events   List all events from JSON database
```

### Installation
1. Install requirements.txt and setup Redis server on your machine.
2. Use CLI tool for managing all data (add emails for reports, manually insert events to google services).
3. Run scheduled script like above.
4. See events in Google Calendar & Keep chosen todo list.
