from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage
from ropon_data.views.pages import ObservingNetworkPageViewSet
from wagtail.admin.ui.tables import UserColumn, Column
from bs4 import BeautifulSoup


User = get_user_model()


class ObservingNetworkPageViewSetTests(WagtailPageTestCase):
    def setUp(self):
        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

        # Create test users with different permissions
        self.superuser = self.create_superuser(
            username='superuser',
            email='super@example.com',
            password='password'
        )

        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )

        self.editor1 = User.objects.create_user(
            username='editor1',
            email='editor1@example.com',
            password='password'
        )

        self.editor2 = User.objects.create_user(
            username='editor2',
            email='editor2@example.com',
            password='password'
        )

        # Create groups and add users
        moderators_group = Group.objects.get(name='Moderators')
        editors_group = Group.objects.get(name='Editors')
        self.moderator.groups.add(moderators_group)
        self.editor1.groups.add(editors_group)
        self.editor2.groups.add(editors_group)

        # Create test observing network pages with different owners
        self.network1 = ObservingNetworkPage(
            title='Network 1',
            name='Network 1',
            abbreviation='N1',
            description='Test network 1',
            website_url='http://example1.com',
            contact='contact1@example.com',
            has_catalog='yes',
            owner=self.editor1
        )
        self.index_page.add_child(instance=self.network1)
        self.network1.save_revision().publish()

        self.network2 = ObservingNetworkPage(
            title='Network 2',
            name='Network 2',
            abbreviation='N2',
            description='Test network 2',
            website_url='http://example2.com',
            contact='contact2@example.com',
            has_catalog='yes',
            owner=self.editor2
        )
        self.index_page.add_child(instance=self.network2)
        self.network2.save_revision().publish()

    def test_viewset_has_owner_column(self):
        """Test that the viewset includes an Owner column in its columns configuration."""
        viewset = ObservingNetworkPageViewSet()

        # Check that Owner column exists in columns
        owner_columns = [col for col in viewset.columns if hasattr(col, 'name') and col.name == 'owner']
        self.assertEqual(len(owner_columns), 1, "Should have exactly one Owner column")

        owner_column = owner_columns[0]

        # Verify it's a UserColumn
        self.assertIsInstance(owner_column, UserColumn, "Owner column should be a UserColumn")

        # Verify column properties
        self.assertEqual(owner_column.label, 'Owner')
        self.assertEqual(owner_column.classname, 'owner')
        self.assertEqual(owner_column.sort_key, 'owner__username')

    def test_viewset_has_abbreviation_column(self):
        """Test that the viewset still includes the Abbreviation column."""
        viewset = ObservingNetworkPageViewSet()

        # Check that Abbreviation column exists in columns
        abbrev_columns = [col for col in viewset.columns if hasattr(col, 'name') and col.name == 'abbreviation']
        self.assertEqual(len(abbrev_columns), 1, "Should have exactly one Abbreviation column")

        abbrev_column = abbrev_columns[0]

        # Verify it's a Column
        self.assertIsInstance(abbrev_column, Column, "Abbreviation column should be a Column")

        # Verify column properties
        self.assertEqual(abbrev_column.label, 'Abbreviation')
        self.assertEqual(abbrev_column.classname, 'abbreviation')
        self.assertEqual(abbrev_column.sort_key, 'abbreviation')

    def test_admin_list_view_displays_owner_column(self):
        """Test that the admin list view displays the Owner column."""
        self.login(self.superuser)

        # Access the admin list view
        response = self.client.get('/admin/observing_networks/')

        self.assertEqual(response.status_code, 200)

        # Check that the response contains owner information
        self.assertContains(response, 'editor1')
        self.assertContains(response, 'editor2')

    def test_owner_column_sorting(self):
        """Test that the Owner column can be sorted."""
        self.login(self.superuser)

        # Test sorting by owner ascending
        response = self.client.get('/admin/observing_networks/?ordering=owner__username')
        self.assertEqual(response.status_code, 200)

        # Test sorting by owner descending
        response = self.client.get('/admin/observing_networks/?ordering=-owner__username')
        self.assertEqual(response.status_code, 200)

    def test_editor_sees_only_own_pages_with_owner_column(self):
        """Test that editors only see their own pages and the Owner column shows correctly."""
        self.login(self.editor1)

        # Access the admin list view as editor1
        response = self.client.get('/admin/observing_networks/')

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the listing results - try different selectors
        listing_area = (
            soup.find('div', id='listing-results') or
            soup.find('div', class_=lambda x: x and 'listing' in x) or
            soup.find('table', class_=lambda x: x and 'listing' in x) or
            soup.find('tbody')
        )

        self.assertIsNotNone(listing_area, "Could not find listing area in the page")

        # Get all table rows in the listing area
        rows = listing_area.find_all('tr')
        listing_text = listing_area.get_text()

        # Should see their own network in the listing
        self.assertIn('Network 1', listing_text, "Editor1 should see their own Network 1 in the listing")

        # Should not see other editor's network in the listing
        self.assertNotIn('Network 2', listing_text, "Editor1 should not see Network 2 in the listing")

        # Count network rows to ensure only one network is displayed
        network_rows = []
        for row in rows:
            row_text = row.get_text()
            if 'Network 1' in row_text or 'Network 2' in row_text:
                network_rows.append(row)

        self.assertEqual(len(network_rows), 1, "Editor1 should see exactly 1 network in the listing")

        # Verify the network row contains the correct network
        network_row = network_rows[0]
        network_row_text = network_row.get_text()
        self.assertIn('Network 1', network_row_text, "The visible network should be Network 1")
        self.assertNotIn('Network 2', network_row_text, "Network 2 should not be visible")

    def test_moderator_sees_all_pages_with_owner_column(self):
        """Test that moderators see all pages and the Owner column shows correctly."""
        self.login(self.moderator)

        # Access the admin list view as moderator
        response = self.client.get('/admin/observing_networks/')

        self.assertEqual(response.status_code, 200)

        # Should see all networks and their owners
        self.assertContains(response, 'Network 1')
        self.assertContains(response, 'Network 2')
        self.assertContains(response, 'editor1')
        self.assertContains(response, 'editor2')

    def test_superuser_sees_all_pages_with_owner_column(self):
        """Test that superusers see all pages and the Owner column shows correctly."""
        self.login(self.superuser)

        # Access the admin list view as superuser
        response = self.client.get('/admin/observing_networks/')

        self.assertEqual(response.status_code, 200)

        # Should see all networks and their owners
        self.assertContains(response, 'Network 1')
        self.assertContains(response, 'Network 2')
        self.assertContains(response, 'editor1')
        self.assertContains(response, 'editor2')

    def test_owner_column_ordering_integration(self):
        """Test that ordering by owner works correctly in the admin interface."""
        self.login(self.superuser)

        # Test ascending order (editor1 comes before editor2 alphabetically)
        response = self.client.get('/admin/observing_networks/?ordering=owner')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the listing results - try different selectors
        listing_area = (
            soup.find('div', id='listing-results') or
            soup.find('div', class_=lambda x: x and 'listing' in x) or
            soup.find('table', class_=lambda x: x and 'listing' in x) or
            soup.find('tbody')
        )

        self.assertIsNotNone(listing_area, "Could not find listing area in the page")

        # Get all table rows that contain our test data
        rows = listing_area.find_all('tr')

        # Find rows containing our networks
        network_rows = []
        for row in rows:
            row_text = row.get_text()
            if 'Network 1' in row_text or 'Network 2' in row_text:
                network_rows.append(row)

        self.assertEqual(len(network_rows), 2, "Should find exactly 2 network rows")

        # Extract the order of networks and their owners
        network_order = []
        for row in network_rows:
            row_text = row.get_text()
            if 'Network 1' in row_text:
                network_order.append(('Network 1', 'editor1'))
            elif 'Network 2' in row_text:
                network_order.append(('Network 2', 'editor2'))

        # In ascending order, editor1 should come before editor2
        self.assertEqual(network_order[0][1], 'editor1', "First network should be owned by editor1 in ascending order")
        self.assertEqual(network_order[1][1], 'editor2', "Second network should be owned by editor2 in ascending order")

        # Test descending order (editor2 comes before editor1)
        response = self.client.get('/admin/observing_networks/?ordering=-owner')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the listing results
        listing_area = (
            soup.find('div', id='listing-results') or
            soup.find('div', class_=lambda x: x and 'listing' in x) or
            soup.find('table', class_=lambda x: x and 'listing' in x) or
            soup.find('tbody')
        )

        self.assertIsNotNone(listing_area, "Could not find listing area for descending order")

        # Get all table rows that contain our test data
        rows = listing_area.find_all('tr')

        # Find rows containing our networks
        network_rows = []
        for row in rows:
            row_text = row.get_text()
            if 'Network 1' in row_text or 'Network 2' in row_text:
                network_rows.append(row)

        self.assertEqual(len(network_rows), 2, "Should find exactly 2 network rows in descending order")

        # Extract the order of networks and their owners
        network_order = []
        for row in network_rows:
            row_text = row.get_text()
            if 'Network 1' in row_text:
                network_order.append(('Network 1', 'editor1'))
            elif 'Network 2' in row_text:
                network_order.append(('Network 2', 'editor2'))

        # In descending order, editor2 should come before editor1
        self.assertEqual(network_order[0][1], 'editor2', "First network should be owned by editor2 in descending order")
        self.assertEqual(network_order[1][1], 'editor1', "Second network should be owned by editor1 in descending order")

    def test_viewset_column_count(self):
        """Test that the viewset has the expected number of columns."""
        viewset = ObservingNetworkPageViewSet()

        # Should have base columns plus abbreviation and owner
        expected_custom_columns = 2  # abbreviation + owner
        base_columns_count = len(viewset.__class__.__bases__[0].columns)

        self.assertEqual(
            len(viewset.columns),
            base_columns_count + expected_custom_columns,
            f"Should have {base_columns_count} base columns + {expected_custom_columns} custom columns"
        )

    def test_owner_column_accessibility(self):
        """Test that the Owner column is accessible to users with different permissions."""
        test_users = [
            (self.superuser, "superuser"),
            (self.moderator, "moderator"),
            (self.editor1, "editor1")
        ]

        for user, user_type in test_users:
            with self.subTest(user_type=user_type):
                self.login(user)
                response = self.client.get('/admin/observing_networks/')
                self.assertEqual(
                    response.status_code,
                    200,
                    f"{user_type} should be able to access the admin list view"
                )

                # All users should see the Owner column header (even if content differs)
                # Note: The exact test depends on how Wagtail renders the column headers
                # This test ensures the view renders successfully with the new column