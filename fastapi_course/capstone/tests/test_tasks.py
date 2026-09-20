def test_a_new_task_has_sensible_defaults(client, make_user, make_project):
    owner = make_user()
    project = make_project(owner)

    response = client.post(f"/projects/{project['id']}/tasks", json={"title": "Write copy"},
                           headers=owner["headers"])

    assert response.status_code == 201
    task = response.json()
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["assignee_id"] is None
    assert task["created_by_id"] == owner["id"]


def test_the_assignee_must_be_a_project_member(client, make_user, make_project):
    owner, stranger = make_user(), make_user()
    project = make_project(owner)

    response = client.post(f"/projects/{project['id']}/tasks",
                           json={"title": "Write copy", "assignee_id": stranger["id"]},
                           headers=owner["headers"])

    assert response.status_code == 422


def test_filtering_by_status_reports_the_total_across_pages(client, make_user, make_project,
                                                            make_task):
    owner = make_user()
    project = make_project(owner)
    for title in ["One", "Two", "Three"]:
        task = make_task(owner, project, title=title)
        if title != "Three":
            client.patch(f"/tasks/{task['id']}", json={"status": "done"}, headers=owner["headers"])

    response = client.get(f"/projects/{project['id']}/tasks?status=done&limit=1",
                          headers=owner["headers"])

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1


def test_sorting_by_priority_puts_high_first(client, make_user, make_project, make_task):
    owner = make_user()
    project = make_project(owner)
    for priority in ["low", "high", "medium"]:
        make_task(owner, project, title=priority, priority=priority)

    response = client.get(f"/projects/{project['id']}/tasks?sort=priority",
                          headers=owner["headers"])

    assert [t["title"] for t in response.json()["items"]] == ["high", "medium", "low"]


def test_overdue_means_past_due_and_not_done(client, make_user, make_project, make_task):
    owner = make_user()
    project = make_project(owner)
    make_task(owner, project, title="Late", due_date="2020-01-01")
    finished = make_task(owner, project, title="Finished late", due_date="2020-01-01")
    client.patch(f"/tasks/{finished['id']}", json={"status": "done"}, headers=owner["headers"])
    make_task(owner, project, title="Future", due_date="2999-01-01")

    response = client.get(f"/projects/{project['id']}/tasks?overdue=true",
                          headers=owner["headers"])

    assert [t["title"] for t in response.json()["items"]] == ["Late"]


def test_patch_changes_only_the_fields_sent(client, make_user, make_project, make_task):
    owner = make_user()
    project = make_project(owner)
    task = make_task(owner, project, title="Keep me", priority="high")

    response = client.patch(f"/tasks/{task['id']}", json={"status": "in_progress"},
                            headers=owner["headers"])

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["title"] == "Keep me"
    assert response.json()["priority"] == "high"


def test_a_null_title_is_rejected(client, make_user, make_project, make_task):
    owner = make_user()
    project = make_project(owner)
    task = make_task(owner, project)

    response = client.patch(f"/tasks/{task['id']}", json={"title": None}, headers=owner["headers"])

    assert response.status_code == 422


def test_members_can_only_delete_tasks_they_created(client, make_user, make_project, make_task):
    owner, member = make_user(), make_user()
    project = make_project(owner, members=[member])
    owners_task = make_task(owner, project)
    members_task = make_task(member, project)

    assert client.delete(f"/tasks/{owners_task['id']}", headers=member["headers"]).status_code == 403
    assert client.delete(f"/tasks/{members_task['id']}", headers=member["headers"]).status_code == 204
    assert client.delete(f"/tasks/{owners_task['id']}", headers=owner["headers"]).status_code == 204


def test_outsiders_get_404_for_a_task(client, make_user, make_project, make_task):
    owner, outsider = make_user(), make_user()
    task = make_task(owner, make_project(owner))

    response = client.get(f"/tasks/{task['id']}", headers=outsider["headers"])

    assert response.status_code == 404
