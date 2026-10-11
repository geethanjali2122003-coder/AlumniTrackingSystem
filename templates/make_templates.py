import os

os.makedirs('templates', exist_ok=True)

# 1. Jobs Page Template
jobs_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Jobs - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>:root { --macfast-maroon: #800000; } body { background-color: #f4f5f7; font-family: 'Segoe UI', sans-serif; }</style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-danger px-4 shadow-sm">
    <a class="navbar-brand fw-bold" href="{% url 'alumni_dashboard' %}"><i class="fa-solid fa-graduation-cap text-warning me-2"></i>MACFAST Portal</a>
    <div class="ms-auto">
        <a href="{% url 'alumni_dashboard' %}" class="btn btn-outline-light btn-sm">Dashboard</a>
    </div>
</nav>

<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-danger">Job Opportunities</h2>
        {% if profile.role == 'alumni' or profile.role == 'faculty' %}
            <a href="{% url 'add_job' %}" class="btn btn-danger fw-bold">+ Post Job</a>
        {% endif %}
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <div class="row g-4">
        {% for job in jobs %}
        <div class="col-md-6">
            <div class="card shadow-sm border-0 p-4 h-100">
                <h4 class="fw-bold text-dark mb-1">{{ job.title }}</h4>
                <h6 class="text-danger fw-semibold">{{ job.company }} &bull; {{ job.location }}</h6>
                <p class="text-muted mt-3 mb-4">{{ job.description }}</p>
                <div class="d-flex justify-content-between align-items-center mt-auto pt-3 border-top">
                    <small class="text-muted"><i class="fa-solid fa-user me-1"></i>Posted by: {{ job.posted_by.first_name }}</small>
                    <a href="mailto:{{ job.contact_email }}" class="btn btn-outline-danger btn-sm font-semibold">Apply via Email</a>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12"><p class="text-muted">No job postings available right now.</p></div>
        {% endfor %}
    </div>
</div>
</body>
</html>"""

# 2. Add Job Page Template
add_job_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Post Job - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light py-5">
<div class="container" style="max-width:600px;">
    <div class="card shadow-sm border-0 p-4">
        <h3 class="fw-bold text-danger mb-4">Post a New Job Opening</h3>
        <form method="POST">
            {% csrf_token %}
            <div class="mb-3">
                <label class="form-label fw-semibold">Job Title</label>
                <input type="text" name="title" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Company Name</label>
                <input type="text" name="company" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Location</label>
                <input type="text" name="location" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Contact Email</label>
                <input type="email" name="contact_email" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Job Description</label>
                <textarea name="description" class="form-control" rows="4" required></textarea>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-danger w-100 fw-bold">Post Job</button>
                <a href="{% url 'job_list' %}" class="btn btn-outline-secondary w-50">Cancel</a>
            </div>
        </form>
    </div>
</div>
</body>
</html>"""

# Write templates
with open('templates/jobs.html', 'w') as f: f.write(jobs_html)
with open('templates/add_job.html', 'w') as f: f.write(add_job_html)

print("TEMPLATES FOR JOBS GENERATED SUCCESSFULLY!")