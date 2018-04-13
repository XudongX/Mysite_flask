from flask import render_template, abort, redirect, request, url_for, flash, send_from_directory
from ..models import FunPic
from flask_login import login_required, current_user
from . import funpic
from .. import db
from .forms import Funpic
from ..decorators import admin_required
from .spider import LinkSaver, Downloader, Spider


@funpic.route('/disable/<id>')
@login_required
@admin_required
def download_disable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/enable/<id>')
@login_required
@admin_required
def download_enable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = False
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/girls', methods=['GET', 'POST'])
def girls():
    form = Funpic()
    query = FunPic.query.filter_by(info='good').filter_by(type='girls')
    if form.validate_on_submit():
        spider = Spider()
        downloader = Downloader(spider)
        ls = LinkSaver(downloader)
        ls.save_to_database()
        redirect(url_for('.girls'))
    pagination = query.order_by(FunPic.timestamp.desc()).paginate(per_page=5)
    links = pagination.items
    return render_template('funpic/funpic.html',
                           form=form,
                           links=links,
                           girls=True,
                           pagination=pagination)


@funpic.route('/funny')
def funny():
    form = Funpic()
    query = FunPic.query.filter_by(info='good').filter_by(type='funny')
    if form.validate_on_submit():
        spider = Spider(url='http://jandan.net/pic')
        downloader = Downloader(spider, mode='rank')
        ls = LinkSaver(downloader)
        ls.save_to_database(type='funny')
        redirect(url_for('.girls'))
    pagination = query.order_by(FunPic.timestamp.desc()).paginate(per_page=5)
    links = pagination.items
    return render_template('funpic/funpic.html',
                           form=form,
                           links=links,
                           girls=False,
                           pagination=pagination)
