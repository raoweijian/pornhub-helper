#!/usr/bin/env python
from app import db, flask_app
from app.models import Task
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

manager = Manager(flask_app)
migrate = Migrate(flask_app, db)


def make_shell_context():
    return dict(flask_app=flask_app, db=db, Task=Task)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
