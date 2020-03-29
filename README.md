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


### Log
```
29/03/20 08:23:41 - MyRedis.Logger - INFO - MyRedis object created successfully
29/03/20 08:23:41 - Moodle.Logger - INFO - MoodleManager object created successfully
29/03/20 08:23:50 - Moodle.Logger - INFO - URL opened in web driver
29/03/20 08:23:53 - Moodle.Logger - INFO - Logged in successfully to Moodle Account
29/03/20 08:23:53 - Moodle.Logger - INFO - Got event #71792 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7790&time=1585563600#event_71792
29/03/20 08:23:53 - Moodle.Logger - INFO - Event #71792 already exists in database
29/03/20 08:23:53 - Moodle.Logger - INFO - Got event #72394 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=8200&time=1585684800#event_72394
29/03/20 08:23:53 - Moodle.Logger - INFO - Event #72394 already exists in database
29/03/20 08:23:53 - Moodle.Logger - INFO - Got event #71828 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7785&time=1585736460#event_71828
29/03/20 08:23:53 - Moodle.Logger - INFO - Event #71828 already exists in database
29/03/20 08:23:53 - Moodle.Logger - INFO - Got event #72471 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7793&time=1586033940#event_72471
29/03/20 08:23:53 - Moodle.Logger - INFO - Event #72471 already exists in database
29/03/20 08:23:54 - Moodle.Logger - INFO - Got event #71793 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7790&time=1586168400#event_71793
29/03/20 08:23:54 - Moodle.Logger - INFO - Event #71793 already exists in database
29/03/20 08:23:54 - Moodle.Logger - INFO - Got event #71829 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7785&time=1586341260#event_71829
29/03/20 08:23:54 - Moodle.Logger - INFO - Event #71829 already exists in database
29/03/20 08:23:54 - Moodle.Logger - INFO - Got event #71821 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7785&time=1586379540#event_71821
29/03/20 08:23:54 - Moodle.Logger - INFO - Event #71821 already exists in database
29/03/20 08:23:54 - Moodle.Logger - INFO - Got event #71794 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7790&time=1586773200#event_71794
29/03/20 08:23:54 - Moodle.Logger - INFO - Event #71794 already exists in database
29/03/20 08:23:55 - Moodle.Logger - INFO - Got event #71795 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7790&time=1587377700#event_71795
29/03/20 08:23:55 - Moodle.Logger - INFO - Event #71795 already exists in database
29/03/20 08:23:55 - Moodle.Logger - INFO - Got event #71796 : https://online.shenkar.ac.il/calendar/view.php?view=day&course=7790&time=1587982500#event_71796
29/03/20 08:23:55 - Moodle.Logger - INFO - Event #71796 already exists in database
29/03/20 08:23:57 - Moodle.Logger - INFO - New Events=0, Weekly Events=0, Total Events in Database=12, All Events=0
29/03/20 08:23:57 - Moodle.Logger - INFO - No new events, nor weekly report needed.

```