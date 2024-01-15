import repository.pages.login
import repository.pages.logout
import repository.pages.registry
import repository.pages.profile
import repository.pages.main_page
import repository.pages.category
import repository.pages.product
import repository.pages.cart
import repository.pages.search
import repository.pages.about
import repository.pages.delivery


class PageInstance:

    def __init__(self, handler, page):
        self.handler = handler
        self.page = page


class Pages:

    def __init__(self):
        self.main_page = PageInstance(
            repository.pages.main_page.MainPage(),
            repository.pages.main_page.main_page,
        )
        self.login = PageInstance(
            repository.pages.login.Login(),
            repository.pages.login.login_page,
        )
        self.logout = PageInstance(
            repository.pages.logout.Logout(),
            repository.pages.logout.logout_page,
        )
        self.registry = PageInstance(
            repository.pages.registry.Registry(),
            repository.pages.registry.registry_page,
        )
        self.profile = PageInstance(
            repository.pages.profile.Profile(),
            repository.pages.profile.profile_page,
        )
        self.category = PageInstance(
            repository.pages.category.Category(),
            repository.pages.category.category_page,
        )
        self.product = PageInstance(
            repository.pages.product.Product(),
            repository.pages.product.product_page,
        )
        self.cart = PageInstance(
            repository.pages.cart.Cart(),
            repository.pages.cart.cart_page,
        )
        self.search = PageInstance(
            repository.pages.search.Search(),
            repository.pages.search.search_page,
        )
        self.about = PageInstance(
            repository.pages.about.About(),
            repository.pages.about.about_page,
        )
        self.delivery = PageInstance(
            repository.pages.delivery.Delivery(),
            repository.pages.delivery.delivery_page,
        )
