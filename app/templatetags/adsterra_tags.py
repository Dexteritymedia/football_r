from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.filter
def ads_after_paragraph(value, arg):

    # Render our adsense code placed in html file
    ad_code = render_to_string("tags/adsterra_ads.html")

    value = str(value)

    # Break down content into paragraphs
    paragraphs = value.split("</p>")

    # Check if paragraph we want to post after exists
    if arg < len(paragraphs):

        # Append our code before the following paragraph
        paragraphs[arg] = ad_code + paragraphs[arg]

        # Assemble our text back with injected adsense code
        value = "</p>".join(paragraphs)

    return value


@register.filter
def ads_in_match_result_page(value, arg):

    # Render our adsense code placed in html file
    ad_code = render_to_string("tags/adsterra_ads.html")

    value = str(value)

    # Break down content into paragraphs
    paragraphs = value.split("</tr>")

    # Check if paragraph we want to post after exists
    if arg < len(paragraphs):

        # Append our code before the following paragraph
        paragraphs[arg] = ad_code + paragraphs[arg]

        # Assemble our text back with injected adsense code
        value = "</tr>".join(paragraphs)

    return value
