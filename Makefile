.PHONY: build run stop logs clean


# Запуск сервисов в фоновом режиме
run:
	docker-compose up -d --build

# Остановка сервисов
stop:
	docker-compose stop

# Подключение к логам всех сервисов
logs:
	docker-compose logs -f

# Удаление всех контейнеров, сетей и томов
clean:
	docker-compose down -v --remove-orphans


# Запуск Dockerfile, создание образа
up:
	docker build -t goods_sales_analyzes_build .

# Запуск образа, создание контейнера
start:
	docker run -d -p 5000:5000 --name goods_sales_analyzes_container goods_sales_analyzes_build

# Просмотр логов в контейнере
log:
	docker logs goods_sales_analyzes_container

