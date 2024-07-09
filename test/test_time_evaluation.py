from work_clock.time_evaluation import BookingTime, TimeBookingList, DailyBookings


def test_booking_time_basics():
    six_ten = BookingTime(6, 10)
    assert six_ten.hours == 6
    assert six_ten.minutes == 10
    assert str(six_ten) == "6:10"

    one_fiftyfive = BookingTime.from_string("01:55")
    assert one_fiftyfive.hours == 1
    assert one_fiftyfive.minutes == 55
    assert str(one_fiftyfive) == "1:55"

    seven_tree_quarters = BookingTime.from_hour_float(7.75)
    assert seven_tree_quarters.hours == 7
    assert seven_tree_quarters.minutes == 45
    assert str(seven_tree_quarters) == "7:45"


def test_booking_time_calculations():
    six_ten = BookingTime(6, 10)
    one_fiftyfive = BookingTime(1, 55)

    total = six_ten + one_fiftyfive
    assert total.hours == 8
    assert total.minutes == 5
    assert str(total) == "8:05"

    diff = six_ten - one_fiftyfive
    assert diff.hours == 4
    assert diff.minutes == 15
    assert str(diff) == "4:15"

    negative = one_fiftyfive - six_ten
    assert negative.hours == -4
    assert negative.minutes == -15
    assert str(negative) == "-4:15"


def test_booking_time_negative():
    zero_ten = BookingTime(0, -10)
    assert zero_ten.hours == 0
    assert zero_ten.minutes == -10
    assert str(zero_ten) == "-0:10"

    one_zero = BookingTime(-1, 0)
    assert one_zero.hours == -1
    assert one_zero.minutes == 0
    assert str(one_zero) == "-1:00"

    one_ten = BookingTime(-1, 10)
    assert one_ten.hours == 0
    assert one_ten.minutes == -50
    assert str(one_ten) == "-0:50"

    one_ten = BookingTime(-1, -10)
    assert one_ten.hours == -1
    assert one_ten.minutes == -10
    assert str(one_ten) == "-1:10"

    one_ten = BookingTime.from_string("-1:10")
    assert one_ten.hours == -1
    assert one_ten.minutes == -10
    assert str(one_ten) == "-1:10"

    one_ten = BookingTime.from_string("-01:10")
    assert one_ten.hours == -1
    assert one_ten.minutes == -10
    assert str(one_ten) == "-1:10"


def test_daily_bookings():
    break_times: TimeBookingList = [
        (BookingTime(9, 15), BookingTime(9, 30)),
        (BookingTime(12, 30), BookingTime(13, 0)),
    ]
    
    both_breaks = [(BookingTime(9, 0), BookingTime(17, 0))]
    assert DailyBookings(both_breaks, break_times).total == BookingTime(7, 15)
    
    one_break = [(BookingTime(10, 15), BookingTime(13, 30))]
    assert DailyBookings(one_break, break_times).total == BookingTime(2, 45)
    
    no_break = [(BookingTime(10, 15), BookingTime(11, 30))]
    assert DailyBookings(no_break, break_times).total == BookingTime(1, 15)

    partial_break_start = [(BookingTime(9, 20), BookingTime(10, 0))]
    assert DailyBookings(partial_break_start, break_times).total == BookingTime(0, 30)
    
    partial_break_end = [(BookingTime(10, 15), BookingTime(12, 50))]
    assert DailyBookings(partial_break_end, break_times).total == BookingTime(2, 15)

    partial_break_both = [(BookingTime(9, 20), BookingTime(12, 50))]
    assert DailyBookings(partial_break_both, break_times).total == BookingTime(3, 0)

    both_breaks_two_bookings = [
        (BookingTime(9, 0), BookingTime(10, 0)),
        (BookingTime(12, 0), BookingTime(13, 30)),
    ]
    assert DailyBookings(both_breaks_two_bookings, break_times).total == BookingTime(1, 45)


def test_daily_bookings_done_time():
    break_times: TimeBookingList = [
        (BookingTime(9, 15), BookingTime(9, 30)),
        (BookingTime(12, 30), BookingTime(13, 0)),
    ]
    too_little: TimeBookingList = [
        (BookingTime(9, 0), BookingTime(10, 0)),  # 0.75 hours
        (BookingTime(10, 30), BookingTime(12, 0)),  # 1.5 hours
    ]
    assert DailyBookings(bookings=too_little, break_times=break_times, normal_hours_per_day=7.0,
                         ).done_for_today == BookingTime(17, 15)
    too_much: TimeBookingList = [
        (BookingTime(6, 0), BookingTime(10, 0)),  # 3.75 hours
        (BookingTime(10, 30), BookingTime(14, 30)),  # 3.5 hours
        (BookingTime(15, 15), BookingTime(18, 00)),  # 2.75 hours
    ]
    assert DailyBookings(bookings=too_much, break_times=break_times, normal_hours_per_day=7.0,
                         ).done_for_today == BookingTime(14, 15)
