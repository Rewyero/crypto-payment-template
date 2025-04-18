from django.shortcuts import render

def docs_home(request):
    return render(request, 'docs/home.html', {
        'section': 'home',
        'title': 'Documentation - CoinFuse'
    })

def getting_started(request):
    return render(request, 'docs/getting_started.html', {
        'section': 'getting_started',
        'title': 'Getting Started - CoinFuse Docs'
    })

def api_reference(request):
    return render(request, 'docs/api_reference.html', {
        'section': 'api_reference',
        'title': 'API Reference - CoinFuse Docs'
    })

def webhooks(request):
    return render(request, 'docs/webhooks.html', {
        'section': 'webhooks',
        'title': 'Webhooks - CoinFuse Docs'
    })

def sdks(request):
    return render(request, 'docs/sdks.html', {
        'section': 'sdks',
        'title': 'SDKs & Libraries - CoinFuse Docs'
    })

def examples(request):
    return render(request, 'docs/examples.html', {
        'section': 'examples',
        'title': 'Examples - CoinFuse Docs'
    })

def changelog(request):
    return render(request, 'docs/changelog.html', {
        'section': 'changelog',
        'title': 'Changelog - CoinFuse Docs'
    })

def faq(request):
    return render(request, 'docs/faq.html', {
        'section': 'faq',
        'title': 'FAQ - CoinFuse Docs'
    }) 