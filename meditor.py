import pkgutil
import importlib
import inspect
import di
from typing import get_args
from di.dependent import Dependent
from diator.mediator import Mediator
from diator.container.di import DIContainer
from diator.requests import RequestHandler, RequestMap 
from di import bind_by_type
from sqlalchemy.orm import Session

import backend.application.handlers as handlers_package 

def build_mediator(db: Session) -> Mediator:
    container = di.Container()
    session_hook = bind_by_type(Dependent(lambda: db, scope="request"), Session)
    container.bind(session_hook)

    request_map = RequestMap()

    for loader, module_name, is_pkg in pkgutil.walk_packages(
        handlers_package.__path__, 
        handlers_package.__name__ + "."
    ):
        module = importlib.import_module(module_name)
        
        for name, obj in inspect.getmembers(module, inspect.isclass):

            if hasattr(obj, "handle") and obj is not RequestHandler:
                

                handler_hook = bind_by_type(Dependent(obj, scope="request"), obj)
                container.bind(handler_hook)

                for base in getattr(obj, "__orig_bases__", []):
                    origin = getattr(base, "__origin__", None)

                    if origin and getattr(origin, "__name__", "") == "RequestHandler":
                        args = get_args(base)
                        if args:
                            command_type = args[0]
                            request_map.bind(command_type, obj)


    di_container = DIContainer() 
    di_container.attach_external_container(container)

    return Mediator(
        request_map=request_map, 
        container=di_container
    )