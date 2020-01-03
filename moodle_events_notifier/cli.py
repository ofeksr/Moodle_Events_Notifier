import click
from moodle_manager import MoodleManager
import translators as ts

moodle = None


def _check_moodle_object():
    global moodle
    if moodle is None:
        try:
            moodle = MoodleManager()
        except Exception:
            moodle = MoodleManager()


@click.group()
def cli():
    """CLI tool for managing Moodle Events Notifier"""
    pass


@cli.command('show_events')
def show_events():
    """List all events from JSON database"""
    _check_moodle_object()

    events = moodle.show_events_from_db()
    results = []

    click.echo('Fetching events from database...')
    with click.progressbar(events.items()) as bar:
        for event_id, details in bar:
            #  translating from hebrew to english using ts.google for echo displaying
            results.append(f'Event ID #{event_id}:\n{ts.google(", ".join(details.values()), "iw", "en")}\n')
    click.echo('\n'.join(results))


@cli.command('insert_event')
@click.option('--agent', prompt='Enter Google agent (keep/calendar)', type=str)
@click.option('--event_id', prompt='Enter event id for insert', type=int)
def insert_event(event_id, agent):
    """Insert event to Google Keep (list) \ Calendar"""
    _check_moodle_object()
    if agent == 'keep':
        moodle.insert_event_keep(event_id=event_id)
    elif agent == 'calendar':
        moodle.insert_event_calendar(event_id=event_id)


@cli.command('show_emails')
def show_email_addresses():
    """List all names and email addresses of scheduled report"""
    for name, email in MoodleManager.show_email_addresses().items():
        click.echo(f'{name}, {email}')


@cli.command('add_email')
@click.option('--name', prompt='Enter email address', type=str)
@click.option('--email_address', prompt=True, type=str)
def add_email_address(name, email_address):
    """Add email address to scheduled report"""
    MoodleManager.add_email_address(name=name, email_address=email_address)


@cli.command('remove_email')
@click.option('--name', prompt='Enter email address')
def remove_email_address(name):
    """Remove email address from scheduled report"""
    MoodleManager.remove_email_address(name=name)


if __name__ == '__main__':
    cli()
