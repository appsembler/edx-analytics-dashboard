import mock

from django.test import TestCase
from django.core.urlresolvers import reverse

import analyticsclient.activity_type as AT
from analyticsclient.exceptions import ClientError

import courses.views as views

class StudentEngagementTestView(TestCase):

    def mock_summary_data(self):
        return {
            'interval_end': '2013-01-01T12:12:12Z',
            AT.ANY: 100,
            AT.ATTEMPTED_PROBLEM: 301,
            AT.PLAYED_VIDEO: 1000,
            AT.POSTED_FORUM: 0,
        }

    def mock_summary_error(self):
        raise ClientError()

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=mock_summary_data, autospec=True))
    def test_engagement_page_success(self):
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # make sure the date is formatted correctly
        self.assertEqual(response.context['summary']['week_of_activity'], 'January 01, 2013')

        # check to make sure that we have tooltips
        self.assertEqual(response.context['tooltips']['all_activity_summary'],
                         'Students who initiated an action.')
        self.assertEqual(response.context['tooltips']['posted_forum_summary'],
                         'Students who created a post, responded to a post, or made a comment in any discussion.')
        self.assertEqual(response.context['tooltips']['attempted_problem_summary'],
                         'Students who answered any question.')
        self.assertEqual(response.context['tooltips']['played_video_summary'],
                         'Students who started watching any video.')

        # check page title
        self.assertEqual(response.context['page_title'], 'Engagement')

        # make sure the summary numbers are correct
        self.assertEqual(response.context['summary'][AT.ANY], 100)
        self.assertEqual(response.context['summary'][AT.ATTEMPTED_PROBLEM], 301)
        self.assertEqual(response.context['summary'][AT.PLAYED_VIDEO], 1000)
        self.assertEqual(response.context['summary'][AT.POSTED_FORUM], 0)

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=ClientError, autospec=True))
    def test_engagement_page_fail(self):
        """
        The course engagement page should raise a 404 when there is an error accessing API data.
        """
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)