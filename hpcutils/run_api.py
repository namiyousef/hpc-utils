import connexion
import os
from hpcutils.config import PORT


def main():
    app = connexion.FlaskApp(__name__, specification_dir='api/specs/')
    app.add_api('api.yaml')
    app.run(port=PORT)


if __name__ == '__main__':
    main()