import importlib
import inspect
import os
from typing import get_args

import di
from di import bind_by_type
from di.dependent import Dependent
from diator.container.di import DIContainer
from diator.mediator import Mediator
from diator.requests import RequestMap
from sqlalchemy.orm import Session


def build_mediator(db: Session) -> Mediator:
    container = di.Container()
    container.bind(bind_by_type(Dependent(lambda: db, scope="request"), Session))
    request_map = RequestMap()
    
    current_path = os.path.abspath(__file__)
    project_root = os.path.dirname(current_path)
    
    for _ in range(5):
        if os.path.exists(os.path.join(project_root, "backend")):
            break
        project_root = os.path.dirname(project_root)

    application_dir = os.path.join(project_root, "backend", "application")

    if not os.path.exists(application_dir):
        return Mediator(request_map=request_map, container=DIContainer())

    for root, _, files in os.walk(application_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), project_root)
                module_name = rel_path.replace(os.sep, ".").removesuffix(".py")
                
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):

                        if hasattr(obj, "handle") and name != "RequestHandler":
                            
                            container.bind(bind_by_type(Dependent(obj, scope="request"), obj))
                            
                            for base in getattr(obj, "__orig_bases__", []):
                                args = get_args(base)
                                if args:
                                    request_type = args[0]
                                    request_map.bind(request_type, obj)
                except Exception:
                    continue
                    
    di_container = DIContainer()
    di_container.attach_external_container(container)
    return Mediator(request_map=request_map, container=di_container)