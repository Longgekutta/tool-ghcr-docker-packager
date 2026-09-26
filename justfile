default:
    @python main.py health

setup:
    @python main.py setup

test:
    @python main.py test

health:
    @python main.py health

clean:
    @python main.py clean

build target="." owner="octocat":
    @python main.py build --target {{target}} --owner {{owner}}

workflow target="." owner="octocat":
    @python main.py workflow --target {{target}} --owner {{owner}}
