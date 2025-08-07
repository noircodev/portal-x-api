from .base import *
PROJECT_ENV = config('PROJECT_ENV', default=None)
PROJECT_ENV = str(PROJECT_ENV).lower() if PROJECT_ENV else None
if PROJECT_ENV == "production":
    from .production import *
elif PROJECT_ENV == 'development':
    from .local import *
elif PROJECT_ENV == 'test':
    pass
else:
    raise EnvironmentError("Project environment was not properly declared")
