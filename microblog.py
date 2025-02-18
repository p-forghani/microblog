import click
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask.cli import with_appcontext

from app import create_app, db
from app.models import Post, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Preload objects into Flask shell."""
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}


# This is the custom shell command.
@click.command('pshell', short_help='Runs ptpython shell in the app context.')
@with_appcontext
def shell_command():
    """Custom Python shell."""
    print("Custom shell is running...")  # Debugging print statement
    try:
        from ptpython.repl import embed  # Try to load ptpython
        embed(globals(), locals())
    except ImportError:
        import code  # Default Python shell
        code.interact(local=dict(globals(), **locals()))


print("Registering custom shell")
# Register the custom shell command
app.cli.add_command(shell_command, name='pshell')

print("custom command registered")
