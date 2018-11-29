from flask import Blueprint, request, current_app
from sqlalchemy import or_
from werkzeug.exceptions import BadRequest

from tblib.model import session
from tblib.handler import json_response, ResponseCode

from ..models import Product, ProductSchema, Shop, ShopSchema

product = Blueprint('product', __name__, url_prefix='/products')


@product.route('', methods=['POST'])
def create_product():
    data = request.get_json()

    product = ProductSchema().load(data)
    session.add(product)
    session.commit()

    return json_response(product=ProductSchema().dump(product))


@product.route('', methods=['GET'])
def product_list():
    shop_id = request.args.get('shop_id', type=int)
    order_direction = request.args.get('order_direction', 'desc')
    limit = request.args.get(
        'limit', current_app.config['PAGINATION_PER_PAGE'], type=int)
    offset = request.args.get('offset', 0, type=int)

    order_by = Product.id.asc() if order_direction == 'asc' else Product.id.desc()
    query = Product.query
    if shop_id is not None:
        query = query.filter(Product.shop_id == shop_id)
    total = query.count()
    query = query.order_by(order_by).limit(limit).offset(offset)

    return json_response(products=ProductSchema().dump(query, many=True), total=total)


@product.route('/<int:id>', methods=['POST'])
def update_product(id):
    data = request.get_json()

    count = Product.query.filter(Product.id == id).update(data)
    if count == 0:
        return json_response(ResponseCode.NOT_FOUND)
    product = Product.query.get(id)
    session.commit()

    return json_response(product=ProductSchema().dump(product))


@product.route('/<int:id>', methods=['GET'])
def product_info(id):
    product = Product.query.get(id)
    if product is None:
        return json_response(ResponseCode.NOT_FOUND)

    return json_response(product=ProductSchema().dump(product))


@product.route('/infos', methods=['GET'])
def product_infos():
    ids = []
    for v in request.args.get('ids', '').split(','):
        id = int(v.strip())
        if id > 0:
            ids.append(id)
    if len(ids) == 0:
        raise BadRequest()

    query = Product.query.filter(Product.id.in_(ids))

    products = {product.id: ProductSchema().dump(product) for product in query}

    return json_response(products=products)
