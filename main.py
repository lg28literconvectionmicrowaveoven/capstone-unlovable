import os
import typer

app = typer.Typer()


@app.command()
def main():
    if not ("prompts" in os.listdir(None) or os.path.exists(".unloved")):
        typer.echo(f"Could not find Unlovable project in {os.getcwd()}")


if __name__ == "__main__":
    app()
