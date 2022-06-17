import connexion
import os


def main():
    app = connexion.FlaskApp(__name__, specification_dir='api/specs/')
    app.add_api('api.yaml')
    app.run(port=8080)


if __name__ == '__main__':
    main()