# multi-messenger-cli
A multi-messenger cli application for whatsapp, telegram and messenger (from facebook)

### Prerequisites

Python 3.10

Modules: 
- Selenium (to navigate through browser applications)
- Pillow (To open images with the default image viewer)

Install modules with:
```
py -3.10 -m pip install pillow==9.1.1 selenium==4.1.5
```

## Usage

To use all supported messenger services in headless browser mode, start with:
```
py -3.10 -m ./path_to_repo/app.py
```


To use a single messenger service (e.g. Telegram) without headless mode:
```
py -3.10 -m pip install ./path_to_repo/telegram_controller.py
```

### Disclaimer

This application is not endorsed by Telegram Messenger Inc. and Meta Platforms Inc. and does not reflect their views or opinions or anyone officially involved in producing or managing Whatsapp, Telegram or Facebook. 
