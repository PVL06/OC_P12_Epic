import click
from rich.prompt import Prompt
from rich.console import Console

from cli_app.controller import Collaborator, Client, Contract, Event

console = Console()
collaborator_ctl = Collaborator()
client_ctl = Client()
contract_ctl = Contract()
event_ctl = Event()


@click.group()
def cli():
    pass


@click.command()
@click.option("-e", "--email", prompt="Email", help="Adresse email pour la connexion")
def login(email):
    password = Prompt.ask("Enter your password", password=True)
    collaborator_ctl.login(email, password)


@click.command()
def logout():
    collaborator_ctl.logout()


@click.command()
@click.option("-c", "--create", is_flag=True, help="Create new collaborator")
@click.option("-u", "--update", is_flag=True, help="Update a collaborator")
@click.option("-d", "--delete", is_flag=True, help="Delete a collaborator")
@click.option("-f", "--filter", type=str, help="filter by role")
def collab(create, update, delete, filter):
    options_selected = sum([create, update, delete])

    if options_selected == 0:
        collaborator_ctl.get_list(filter=filter)

    elif options_selected == 1:
        if create:
            collaborator_ctl.create_collab()
        elif update:
            collaborator_ctl.update_collab(filter=filter)
        elif delete:
            collaborator_ctl.delete_collab(filter=filter)
    else:
        console.print("Multiple options not allowed", style="red")


@click.command()
@click.option("-c", "--create", is_flag=True, help="Create new client")
@click.option("-u", "--update", is_flag=True, help="Update a client")
@click.option("-f", "--filter", is_flag=True, help="filter clients without an assigned commercial")
def client(create, update, filter):
    options_selected = sum([create, update])

    if options_selected == 0:
        client_ctl.get_list(filter=filter)

    elif options_selected == 1:
        if create:
            client_ctl.create_client()
        elif update:
            client_ctl.update_client()
    else:
        console.print("Multiple options not allowed", style="red")


@click.command()
@click.option("-c", "--create", is_flag=True, help="Create new contract")
@click.option("-u", "--update", is_flag=True, help="Update a contract")
@click.option("-f", "--filter", type=str, help="filter contract no signed (no_signed) or debtor client (debtor) ")
def contract(create, update, filter):
    options_selected = sum([create, update])

    if options_selected == 0:
        contract_ctl.get_list(filter)

    elif options_selected == 1:
        if create:
            contract_ctl.create_contract()
        elif update:
            contract_ctl.update_contract()
    else:
        console.print("Multiple options not allowed", style="red")


@click.command()
@click.option("-c", "--create", is_flag=True, help="Create new event")
@click.option("-u", "--update", is_flag=True, help="Update a event")
def event(create, update):
    options_selected = sum([create, update])

    if options_selected == 0:
        event_ctl.get_list()

    elif options_selected == 1:
        if create:
            event_ctl.create_event()
        elif update:
            event_ctl.update_event()
    else:
        console.print("Multiple options not allowed", style="red")


commands = [login, logout, collab, client, contract, event]

for command in commands:
    cli.add_command(command)

if __name__ == "__main__":
    cli()
