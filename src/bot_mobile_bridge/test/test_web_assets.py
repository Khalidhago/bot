"""Sanity checks on the web UI so a bad edit can't silently break phone teleop."""
import os
import re

WEB_DIR = os.path.join(os.path.dirname(__file__), '..', 'web')


def read_index():
    with open(os.path.join(WEB_DIR, 'index.html'), encoding='utf-8') as f:
        return f.read()


def test_index_exists():
    assert os.path.isfile(os.path.join(WEB_DIR, 'index.html'))


def test_publishes_expected_topic():
    html = read_index()
    assert "'/cmd_vel_mobile'" in html
    assert 'geometry_msgs/msg/Twist' in html


def test_is_self_contained():
    """The page must work on the robot's LAN with no internet: no external
    scripts, stylesheets, or fonts."""
    html = read_index()
    assert not re.search(r'src=["\']https?://', html)
    assert not re.search(r'href=["\']https?://', html)


def test_mobile_viewport_set():
    assert 'name="viewport"' in read_index()


def test_speed_limits_match_base_config():
    """UI speed cap must not exceed what bot_base enforces (0.6 m/s)."""
    match = re.search(r'MAX_LINEAR\s*=\s*([\d.]+)', read_index())
    assert match, 'MAX_LINEAR constant missing from index.html'
    assert float(match.group(1)) <= 0.6
