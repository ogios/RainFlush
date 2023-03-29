import USER
import RUN_TMP
import click
import os


@click.command()
@click.option("-u", type=str, default="", help="学号")
def main(u):
    print(f"当前pid: {os.getpid()}")
    us = USER.User(u)
    cookie = us.getCookie()
    run = RUN_TMP.run(cookie)
    if run.getCourses():
        run.chooseCourse()
        if run.getVideo():
            if run.getUndone():
                run.flushALL()


if __name__ == "__main__":
    main()
