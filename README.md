# meuParlamento backend api
> This project provides the HTTP API with endpoints for the [mobile app](https://github.com/meuparlamento/react-native-app)

Backend-api provides endpoints to request random proposals, authors and news.

### Requirements

* [Python 3.7](https://www.python.org/)
* [Docker](https://www.docker.com/)
* [docker-compose](https://docs.docker.com/compose/)
* [Mongodb](https://www.mongodb.com/)

## Installation using Docker

Our docker-compose descriptor takes care of everything providing mongodb intance and backend-api HTTP interface. Make sure you have installed docker and docker-compose.

```sh
$ docker-compose up
```

Test if the HTTP interface is up and running:

```sh
$ curl http://localhost:8000/
{"hello": "meuParlamento.pt"}
```

## Data import

Once you have mongodb up and running you can import the data available at [https://github.com/meuparlamento/open-data](https://github.com/meuparlamento/open-data).

```sh
$ git clone https://github.com/meuparlamento/open-data
$ mongoimport --db meuParlamento --collection proposals --file open-data/proposals.json
```

## Manual installation

In case you prefer not to use Docker we recommend creating a python environment and installing all python requirements:

```sh
pip install -r requirements.txt
```

## Running app.py

This project is based on a microframework called [Chalice](https://github.com/aws/chalice/), a Python Serverless Microframework for AWS. Chalice allows you to quickly create and deploy applications that use [Amazon Lambda](https://aws.amazon.com/lambda/). For more information on how to setup and deploy this project to Amazon AWS please check https://github.com/aws/chalice/. 

In order to run it locally just type:

```sh
chalice local --port 9000 --stage manual 
```


Our docker description takes care of mongodb instance and url. If you need to customize it,  
edit [.chalice/config.json](https://github.com/meuparlamento/meuparlamento-backend-api/.chalice/config.json). To illustrate it, if you have a local mongodb instance please edit `MONGODB_URI` value (e.g. `mongodb://localhost:27017`).

```json
{
    "version": "2.0",
    "app_name": "meuparlamento-backend-api",
    "stages": {
      "manual": {
        "api_gateway_stage": "manual",
        "environment_variables": {
          "MONGODB_URI": "mongodb://localhost:27017",
          "DB_NAME":"meuParlamento"
        }
      }
    }
  }
```

## Testing
To run tests you can use [pytest](https://pytest.org):

```sh
pytest
```

## Meta

Team meuParlamento.pt dev@meuparlamento.pt

Distributed under the GPL license. See ``LICENSE`` for more information.

[https://github.com/meuparlamento](https://github.com/meuparlamento)

## Contributing

1. Fork it (<https://github.com/meuparlamento/meuparlamento-backend-api/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
