from flask import Blueprint, render_template, request
from app.models import Project, Sprint, Task, Issue

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Main route that renders the dashboard page showing project cards
    
    This loads all projects and passes them to the dashboard template.
    The dashboard serves as the entry point to the application.
    """
    # Query all projects
    projects = Project.query.order_by(Project.created_at.desc()).all()
    
    # Render the dashboard template
    return render_template('dashboard.html', projects=projects)

@main_bp.route('/projects')
def projects():
    """
    Route that renders the projects page showing detailed project views
    
    This loads all projects and passes them to the index template.
    The projects page shows the full project details including sprints, tasks, and issues.
    
    When called with partial=True, it renders only specific parts of the page
    for AJAX updates without requiring a full page reload.
    """
    # Query all projects
    projects = Project.query.order_by(Project.created_at.desc()).all()
    
    # Check if this is a partial content request
    partial = request.args.get('partial')
    
    if partial:
        # Handle partial content requests for AJAX updates
        if partial == 'project_sprints':
            # Return sprints for a specific project
            project_id = request.args.get('project_id')
            if project_id:
                project = Project.query.get(project_id)
                if project:
                    return render_template('partials/project_sprints.html', project=project)
            return '', 404
        
        elif partial == 'sprint':
            # Return a specific sprint
            sprint_id = request.args.get('sprint_id')
            if sprint_id:
                sprint = Sprint.query.get(sprint_id)
                if sprint:
                    return render_template('partials/sprint.html', sprint=sprint)
            return '', 404
    
    # Render the full index template with all projects
    return render_template('index.html', projects=projects)

@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    """
    Route that renders a single project page
    
    This loads a specific project by ID and passes it to the project_detail template.
    If the project is not found, returns a 404 error.
    """
    # Query the project by ID
    project = Project.query.get_or_404(project_id)
    
    # Render the project detail template
    return render_template('project_detail.html', project=project)

@main_bp.route('/project/<int:project_id>/sprint/<int:sprint_id>')
def sprint_detail(project_id, sprint_id):
    """
    Route that renders a single sprint within a project context
    
    This loads a specific sprint by ID within a specific project context
    and renders it on a dedicated page. This provides a focused view of
    a single sprint with all its tasks and issues.
    
    Args:
        project_id: ID of the project the sprint belongs to
        sprint_id: ID of the sprint to display
        
    Returns:
        Rendered sprint_detail.html template with sprint and project context
    """
    # Verify the project exists
    project = Project.query.get_or_404(project_id)
    
    # Get the sprint and verify it belongs to this project
    sprint = Sprint.query.get_or_404(sprint_id)
    
    # Ensure the sprint belongs to the specified project
    if sprint.project_id != project_id:
        return "Sprint not found in this project", 404
    
    # Render the sprint detail in project context
    # Pass is_sprint_detail=True to tell the sprint template not to make the sprint collapsible
    return render_template('sprint_detail.html', project=project, sprint=sprint, is_sprint_detail=True)
