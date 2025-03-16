import click
from rich.prompt import Prompt
from rich.console import Console

from cli_app.ctl_collab import Collaborator

console = Console()
collaborator = Collaborator()


@click.group()
def cli():
    pass


@click.command()
@click.option("-e", "--email", prompt="Email", help="Adresse email pour la connexion")
def login(email):
    password = Prompt.ask("Enter your password", password=True)
    collaborator.login(email, password)


@click.command()
def logout():
    collaborator.logout()


@click.command()
@click.option("-c", "--create", is_flag=True, help="Create new collaborator")
@click.option("-u", "--update", is_flag=True, help="Update a collaborator")
@click.option("-d", "--delete", is_flag=True, help="Delete a collaborator")
def collab(create, update, delete):
    options_selected = sum([create, update, delete])

    if options_selected == 0:
        collaborator.get_list()

    elif options_selected == 1:
        if create:
            collaborator.create_collab()
        elif update:
            collaborator.update_collab()
        elif delete:
            collaborator.delete_collab()
    else:
        console.print("Multiple options not allowed", style="red")


commands = [
    login,
    logout,
    collab
]

for command in commands:
    cli.add_command(command)

if __name__ == "__main__":
    cli()
