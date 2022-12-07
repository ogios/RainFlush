import USER
import RUN
import click
import os


@click.command()
@click.option("-u", type=str, help="学号")
def main(u):
    print(f"当前pid: {os.getpid()}")
    us = USER.User(u)
    cookie = us.getCookie()
    run = RUN.run(cookie)
    if run.getCourses():
        run.chooseCourse()
        if run.getCuts():
            if run.getVideo():
                if run.getUndone():
                    run.readContent()
                    run.flushALL()


if __name__ == "__main__":
    main()
