def test_the_creator_becomes_the_owner(client, make_user):
    owner = make_user()

    response = client.post("/projects", json={"name": "Launch"}, headers=owner["headers"])

    assert response.status_code == 201
    assert response.json()["members"] == [
        {"user_id": owner["id"], "email": owner["email"], "full_name": None, "role": "owner"}]


def test_the_project_list_only_shows_my_projects(client, make_user, make_project):
    sidd, ana = make_user(), make_user()
    make_project(sidd, name="Sidd's project")
    make_project(ana, name="Ana's project")

    response = client.get("/projects", headers=sidd["headers"])

    assert [p["name"] for p in response.json()] == ["Sidd's project"]


def test_outsiders_get_404_for_a_project(client, make_user, make_project):
    owner, outsider = make_user(), make_user()
    project = make_project(owner)

    response = client.get(f"/projects/{project['id']}", headers=outsider["headers"])

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_an_added_member_can_see_the_project(client, make_user, make_project):
    owner, member = make_user(), make_user()
    project = make_project(owner, members=[member])

    response = client.get(f"/projects/{project['id']}", headers=member["headers"])

    assert response.status_code == 200
    assert [m["role"] for m in response.json()["members"]] == ["owner", "member"]


def test_adding_an_unknown_email_is_404(client, make_user, make_project):
    owner = make_user()
    project = make_project(owner)

    response = client.post(f"/projects/{project['id']}/members",
                           json={"email": "nobody@example.com"}, headers=owner["headers"])

    assert response.status_code == 404


def test_adding_someone_twice_is_409(client, make_user, make_project):
    owner, member = make_user(), make_user()
    project = make_project(owner, members=[member])

    response = client.post(f"/projects/{project['id']}/members",
                           json={"email": member["email"]}, headers=owner["headers"])

    assert response.status_code == 409


def test_members_cannot_rename_the_project(client, make_user, make_project):
    owner, member = make_user(), make_user()
    project = make_project(owner, members=[member])

    response = client.patch(f"/projects/{project['id']}", json={"name": "Mine now"},
                            headers=member["headers"])

    assert response.status_code == 403


def test_the_owner_can_rename_the_project(client, make_user, make_project):
    owner = make_user()
    project = make_project(owner)

    response = client.patch(f"/projects/{project['id']}", json={"name": "Relaunch v2"},
                            headers=owner["headers"])

    assert response.status_code == 200
    assert response.json()["name"] == "Relaunch v2"


def test_the_owner_cannot_be_removed(client, make_user, make_project):
    owner = make_user()
    project = make_project(owner)

    response = client.delete(f"/projects/{project['id']}/members/{owner['id']}",
                             headers=owner["headers"])

    assert response.status_code == 400


def test_removing_a_member_unassigns_their_tasks(client, make_user, make_project, make_task):
    owner, member = make_user(), make_user()
    project = make_project(owner, members=[member])
    task = make_task(owner, project, assignee_id=member["id"])

    response = client.delete(f"/projects/{project['id']}/members/{member['id']}",
                             headers=owner["headers"])

    assert response.status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=owner["headers"]).json()["assignee_id"] is None
    assert client.get(f"/projects/{project['id']}", headers=member["headers"]).status_code == 404


def test_deleting_a_project_deletes_its_tasks(client, make_user, make_project, make_task):
    owner = make_user()
    project = make_project(owner)
    task = make_task(owner, project)

    response = client.delete(f"/projects/{project['id']}", headers=owner["headers"])

    assert response.status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=owner["headers"]).status_code == 404
