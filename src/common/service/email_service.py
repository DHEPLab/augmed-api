from os import path
from typing import List

import boto3
from botocore.exceptions import ClientError
from mako.template import Template

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)

CHARSET = "UTF-8"
SENDER = "DHEP Lab <dhep.lab@gmail.com>"


def render_template(template_file, **kwargs):
    try:
        template = Template(filename=template_file)
        output = template.render(**kwargs)
    except Exception as e:
        print(e)
        raise BusinessException(BusinessExceptionEnum.RenderTemplateError)
    else:
        return output


def send_email(
    subject: str, to_addresses: List[str], html_template_name: str, **kwargs
):
    session = boto3.session.Session(region_name="us-east-1")
    client = session.client("ses")

    credentials = session.get_credentials().get_frozen_credentials()
    print("token", credentials.token)
    body_html = render_template(
        path.join(path.dirname(__file__), f"templates/{html_template_name}"), **kwargs
    )

    try:
        response = client.send_email(
            Source=SENDER,
            Destination={
                "ToAddresses": to_addresses,
            },
            Message={
                "Subject": {
                    "Charset": CHARSET,
                    "Data": subject,
                },
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": body_html,
                    },
                },
            },
        )

    except Exception as e:
        if isinstance(e, ClientError):
            print(e.response["Error"]["Message"])
        print("Exception: ", e)
        raise BusinessException(BusinessExceptionEnum.SendEmailError, e)
    else:
        return response["MessageId"]
