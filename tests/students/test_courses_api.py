import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()



@pytest.fixture
def course_factory():
    students_set = baker.prepare(Student, _quantity=5)

    def factory(*args, **kwargs):
        return baker.make(Course, students=students_set, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_course(client, course_factory):
    course = course_factory(_quantity=1)

    response = client.get('/api/v1/courses/' + str(course[0].id) + '/')

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == course[0].id


@pytest.mark.django_db
def test_get_courses(client, course_factory):
    courses = course_factory(_quantity=10)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name


@pytest.mark.django_db
def test_filter_courses_id(client, course_factory):
    course_factory(_quantity=10, id=3)

    response = client.get('/api/v1/courses/?id=3')

    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == 3


@pytest.mark.django_db
def test_filter_courses_name(client, course_factory):
    course_factory(_quantity=10, name='Python')

    response = client.get('/api/v1/courses/?name=Python')

    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data[0]['name'] == 'Python'


@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()

    response = client.post('/api/v1/courses/', data={'name': 'test_course'})

    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course_factory(_quantity=1, id=1, name='first name')

    response = client.patch('/api/v1/courses/1/', data={'name': 'second name'})

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'second name'


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    course_factory(_quantity=1, id=1)
    count = Course.objects.count()

    response = client.delete('/api/v1/courses/1/')

    assert response.status_code == 204
    assert Course.objects.count() == count - 1
