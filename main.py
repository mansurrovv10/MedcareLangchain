from fastapi import FastAPI
from mysite.api import auth,users,chat,doctors,schedules,appointments
from mysite.chain import ai
import uvicorn
from mysite.database.db import *

medcare_app = FastAPI(title="MedCare")
medcare_app.include_router(ai.search_router)
medcare_app.include_router(auth.auth_router)
medcare_app.include_router(users.user_router)
medcare_app.include_router(chat.router)
medcare_app.include_router(schedules.router)
medcare_app.include_router(appointments.router)
medcare_app.include_router(doctors.router)

Base.metadata.create_all(bind=engine)



if __name__ == "__main__":
    uvicorn.run(medcare_app, host="127.0.0.1", port=8000)