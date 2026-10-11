import os

os.makedirs('templates', exist_ok=True)

# Directory Page
directory_html = """<!DOCTYPE html>
<html>
<head>
    <title>Directory - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-danger">MACFAST Member Directory</h2>
        <a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary">Dashboard</a>
    </div>
    <div class="card shadow-sm border-0 p-3">
        <table class="table table-hover align-middle">
            <thead class="table-dark">
                <tr>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Department</th>
                    <th>Contact</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {% for p in profiles %}
                <tr>
                    <td class="fw-bold">{{ p.user.first_name }}</td>
                    <td><span class="badge bg-danger text-capitalize">{{ p.role }}</span></td>
                    <td>{{ p.department.name }}</td>
                    <td>{{ p.user.email }}<br><small class="text-muted">{{ p.phone }}</small></td>
                    <td>
                        {% if p.role == 'alumni' %}{{ p.company }} ({{ p.designation }})
                        {% elif p.role == 'student' %}Semester: {{ p.current_semester }}
                        {% elif p.role == 'faculty' %}Faculty ID: {{ p.employee_id }}{% endif %}
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="text-center text-muted">No approved members found.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
</body>
</html>"""

# Jobs Page
jobs_html = """<!DOCTYPE html>
<html>
<head>
    <title>Jobs - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-danger">Job Opportunities</h2>
        <div>
            <a href="{% url 'add_job' %}" class="btn btn-danger fw-bold">+ Post Job</a>
            <a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary ms-2">Dashboard</a>
        </div>
    </div>
    {% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }}">{{ message }}</div>{% endfor %}{% endif %}
    <div class="row g-4">
        {% for job in jobs %}
        <div class="col-md-6">
            <div class="card shadow-sm border-0 p-4">
                <h4 class="fw-bold text-dark">{{ job.title }}</h4>
                <h6 class="text-danger">{{ job.company }} - {{ job.location }}</h6>
                <p class="text-muted mt-2">{{ job.description }}</p>
                <hr>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">Posted by: {{ job.posted_by.first_name }}</small>
                    <a href="mailto:{{ job.contact_email }}" class="btn btn-outline-danger btn-sm">Apply / Email</a>
                </div>
            </div>
        </div>
        {% empty %}
        <p class="text-muted">No job postings available.</p>
        {% endfor %}
    </div>
</div>
</body>
</html>"""

# Events Page
events_html = """<!DOCTYPE html>
<html>
<head>
    <title>Events - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-danger">Upcoming Events</h2>
        <a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary">Dashboard</a>
    </div>
    {% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }}">{{ message }}</div>{% endfor %}{% endif %}
    <div class="row g-4">
        {% for event in events %}
        <div class="col-md-6">
            <div class="card shadow-sm border-0 p-4">
                <h4 class="fw-bold text-dark">{{ event.title }}</h4>
                <p class="text-danger fw-semibold mb-1">Date: {{ event.date }} | Location: {{ event.location }}</p>
                <p class="text-muted">{{ event.description }}</p>
                <a href="{% url 'register_event' event.id %}" class="btn btn-warning fw-bold text-dark w-100">RSVP / Register</a>
            </div>
        </div>
        {% empty %}
        <p class="text-muted">No upcoming events.</p>
        {% endfor %}
    </div>
</div>
</body>
</html>"""

with open('templates/directory.html', 'w') as f: f.write(directory_html)
with open('templates/jobs.html', 'w') as f: f.write(jobs_html)
with open('templates/events.html', 'w') as f: f.write(events_html)

print("MISSING TEMPLATES CREATED SUCCESSFULLY!")