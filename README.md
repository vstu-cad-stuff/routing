[Routing Project](https://vstu-cad-stuff.github.io/routing/)
===============

[Карта с последними данными](https://vstu-cad-stuff.github.io/routing/geojson/)

### Старый функционал
* [correspondence_counter.py](src/correspondence_counter.py): скрипт для подсчёта матрицы корреспонденций
* [correspondence_draw.py](src/correspondence_draw.py): скрипт для отрисовки матрицы корреспонденций
* [path_finding.py](src/path_finding.py): простая версия "жадного" алгоритма по обходу кластеров
* [path_finding_upd.py](src/path_finding_upd.py): модификация предыдущего алгоритма для работы с "реальными" данными
* [path_finding_opt.py](src/path_finding_opt.py): измененная реализация предыдущей версии поддерживающая построение полноценного маршрута
* [path_finding_rnd.py](src/path_finding_rnd.py): генерация маршрута на основе ГСПЧ
* [routing_methods.py](src/routing_methods.py): реализация методов коммивояжёра для обхода кластеров (пока только метод отжига)
* [data/points](./data/points.txt): координаты центров кластеров

----

### Новый функционал
* [main_algorithm.py](main_algorithm.py): модуль по построению маршрута на основе генетических алгоритмов
* [auxiliary.py](auxiliary.py): модуль со вспомогательными функциями
* [data_loader.py](data_loader.py): модуль по загрузке данных из файлов
* [greedy_algorythm.py](greedy_algorithm.py): модуль реализующий 'жадный' алгоритм
* [short_path.py](short_path.py): модулья по построению маршрутов на основе нескольких алгоритмов
 * выпуклая оболочка по [алгоритму Грэхема](https://ru.wikipedia.org/wiki/Алгоритм_Грэхема)
 * поиск терминальных кластеров по принадлежности точки к окружности
 * построение маршрутов по [следующему алгоритму](https://docs.google.com/document/d/1c-BmRMmi4ao1p-muU8SLxFz1QyGHmu_mYOXHvDBXHcQ)