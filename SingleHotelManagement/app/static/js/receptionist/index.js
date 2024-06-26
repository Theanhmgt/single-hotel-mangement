$(document).ready(function () {
      //-------------Đổi định dạng tien---------------
      $('.price').each(function() {
        // Lấy giá trị hiện tại
        var value = $(this).text();

        // Chuyển đổi giá trị thành số
        var number = parseFloat(value);

        // Định dạng lại giá trị
        var formattedValue = number.toLocaleString('vi-VN', {
            style: 'currency',
            currency: 'VND'
        });

        // Gán lại giá trị mới vào phần tử
        $(this).text(formattedValue);
    });

    //------------------Filter tất cả booking hiện tại--------------
    $('.list-booking-checkbox').change(() => {
        const checkedValues = $('input[type="checkbox"]:checked').map(function () {
            return this.value;
        }).get();
        let newUrl = ''
        if ($('input[type="checkbox"]:checked').length > 0) {
            // Tạo URL mới dựa trên các giá trị được chọn
            const params = 'trang-thai=' + checkedValues.join(',');
            newUrl = window.location.pathname + '?' + params;
        } else {
            newUrl = window.location.pathname
        }
        window.location.href = newUrl;
    })
    //--------------Xoa bo loc-----------------
    $('.clear-check-input-btn').click(() => {
        const newUrl = window.location.pathname;
        window.location.href = newUrl;
    })
    //--------------Dong form thanh toan--------------
    $(".close-search-room-form").click(function () {
        $(".overlay-payment").fadeOut();
        $(".payment-form").fadeOut();
    });

        // ----------------- Show modal booking form -----------------
//    $(".confirm-booking-online-btn").click(function () {
//        $(".overlay-booking-form").fadeIn();
//        $(".modal-booking-form").fadeIn();
//    });
//
//    $(".close-modal-booking-form").click(function () {
//        $(".overlay-booking-form").fadeOut();
//        $(".modal-booking-form").fadeOut();
//    });
//
//    $("#print-booking-form-btn").click(function () {
//        var printSection = $("#print-section");
//        if (printSection) {
//            var printSection = document.createElement("div");
//            printSection.id = "printSection";
//            document.body.appendChild(printSection);
//        }
//
//        $("#print-booking-form").clone().appendTo("#printSection");
//        window.print();
//
//        $(".overlay-booking-form").fadeOut();
//        $(".modal-booking-form").fadeOut();
//
//    });
//
//
//    // ----------------- Show modal leasing form -----------------
//    $(".confirm-leasing-btn").click(function () {
//        $(".overlay-leasing-form").fadeIn();
//        $(".modal-leasing-form").fadeIn();
//    });
//
//    $(".close-modal-leasing-form").click(function () {
//        $(".overlay-leasing-form").fadeOut();
//        $(".modal-leasing-form").fadeOut();
//    });
//
//    $("#print-leasing-form-btn").click(function () {
//        var printSection = $("#print-section");
//        if (printSection) {
//            var printSection = document.createElement("div");
//            printSection.id = "printSection";
//            document.body.appendChild(printSection);
//        }
//
//        $("#print-leasing-form").clone().appendTo("#printSection");
//        window.print();
//
//        $(".overlay-leasing-form").fadeOut();
//        $(".modal-leasing-form").fadeOut();
//
//    });

});

$(window).on('load', function () {
    //--------------------Nếu tải lại trang mà đang có param thì checked vào checkbox tương ứng-------------
    var urlParams = new URLSearchParams(window.location.search);
    let statusParam = urlParams.get('trang-thai');
    if (statusParam) {
        statusParam.split(',').forEach(status => {
            var value = Number(status)
            $(`input[type="checkbox"][value="${value}"]`).prop('checked', true);
        })
    }
});

change_booking_status = (booking_id, status) => {
    if (status == 4) {
            Swal.fire({
                title: 'Bạn có chắc muốn huỷ đơn đặt phòng này?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Xác nhận',
                cancelButtonText: 'Huỷ bỏ'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch("/api/receptionist/change-booking-status/", {
                        method: 'post',
                        body: JSON.stringify({
                            'booking_id': booking_id,
                            'status': status
                        }),
                        headers: {
                            'Accept': 'application/json',
                            'Context-Type': 'application/json',
                        }
                    }).then(res => res.json()).then(data => {
                        window.location.reload();
                    })
                }
            })
    } else {
        fetch("/api/receptionist/change-booking-status/", {
            method: 'post',
            body: JSON.stringify({
                'booking_id': booking_id,
                'status': status
            }),
            headers: {
                'Accept': 'application/json',
                'Context-Type': 'application/json',
            }
        }).then(res => res.json()).then(data => {
            window.location.reload();
        })
    }
}

check_out = (booking_id) => {
    fetch("/api/receptionist/check_out/", {
        method: 'post',
        body: JSON.stringify({
            'booking_id': booking_id,
        }),
        headers: {
            'Accept': 'application/json',
            'Context-Type': 'application/json',
        }
    }).then(res => res.json()).then(data => {
        // 00: paid, 01: unpaid
        if (data == '00') {
            Swal.fire({
                title: 'Nhận Phòng Thành Công',
                icon: 'success',
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Xác nhận',
            }).then((result) => { window.location.reload();})
        } else {
            Swal.fire({
                title: 'Trả phòng và thanh toán?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Xác nhận',
                cancelButtonText: 'Huỷ bỏ'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/api/booking/${booking_id}`, {
                        method: 'get',
                    }).then(res => res.json()).then(data => {
                        var booking = data.booking
                        var booking_details = data.booking_details
                        var target = $('.payment-info-row')
                        var row = ''
                        booking_details.map(b => {
                            row += `
                                <tr>
                                    <td>${booking.id}</td>
                                    <td><span class="bg-green-100 text-green-800 text-sm font-medium me-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300"
                                        >${b.room_name}</span
                                    ></td>
                                    <td>${moment(booking.start_date).format('LLL')}</td>
                                    <td>${moment(booking.end_date).format('LLL')}</td>
                                    <td>${b.booking_detail.num_normal_guest}</td>
                                    <td>${b.booking_detail.num_foreigner_guest}</td>
                                    <td>${b.price}</td>
                                </tr>
                            `
                        })
                        target.html(row)
                        $('.payment-form-table-body').html(row)
                        $(".overlay-payment").fadeIn();
                        $(".payment-form").fadeIn();
                    })
                    // Lưu booking_id để gọi api từ một chỗ khác
                    localStorage.setItem('payment-booking', booking_id);
                }
            })
        }
    })
}

function handlePayment() {
    var booking_id = localStorage.getItem('payment-booking')
    if (booking_id) {
        fetch("/api/receptionist/payment/", {
        method: 'post',
        body: JSON.stringify({
            'booking_id': booking_id,
            'payment_method':$('input[type="radio"][name="payment-method"]:checked').val(),
            'additional_action': 'CHECK_OUT'
        }),
        headers: {
            'Accept': 'application/json',
            'Context-Type': 'application/json',
        }
        }).then(res => res.json()).then(data => {
        // 00: lỗi, 01: thanh toán thành công, 02: chưa hỗ trợ thanh toán bằng phương thức đó,
            console.log(data)
            switch (data) {
                case '00':
                    Swal.fire({
                            title: 'Thanh Toán Thất Bại',
                            text:'Hãy thử lại sau',
                            icon: 'warning',
                            confirmButtonColor: '#3085d6',
                            confirmButtonText: 'Xác nhận',
                    })
                    break;
                case '01':
                    Swal.fire({
                            title: 'Thanh Toán Thành Công',
                            text:'In hoá đơn?',
                            showCancelButton: true,
                            icon: 'success',
                            confirmButtonColor: '#3085d6',
                            cancelButtonColor: '#d33',
                            confirmButtonText: 'Xác nhận',
                            cancelButtonText: 'Huỷ bỏ'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            var currentURL = window.location.origin;
                            window.location.href = `${currentURL}/bill/${booking_id}`;
                        } else {
                            const newUrl = window.location.pathname;
                            window.location.href = newUrl;
                        }
                    })
                    break
                case '02':
                    Swal.fire({
                            title: 'Hiện chưa hỗ trợ phương thức thanh toán này',
                            text:'Hãy thử lại với phương thức khác',
                            icon: 'warning',
                            confirmButtonColor: '#3085d6',
                            confirmButtonText: 'Xác nhận',
                    })
                    break;
                default:
                    window.location.href = data
            }
        })
    } else {
        Swal.fire({
                title: 'Thanh Toán Thất Bại',
                text:'Hãy thử lại sau',
                icon: 'warning',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'Xác nhận',
        })
    }
}

function calculate_booking_time(start_date, end_date) {
    var startdate = moment(start_date);
    var enddate = moment(end_date);
    if (startdate.isValid() && enddate.isValid()) {
        var duration = moment.duration(enddate.diff(startdate));
        var days = duration.days();
        var hours = duration.hours();

        var total_time = '';

        if (days > 0) {
            total_time += days + ' ngày ';
        }
        if (hours > 0) {
            total_time += hours + ' giờ';
        }
        if (days === 0 && hours === 0) {
            total_time = '0 giờ';
        }
        return total_time
    }
    return ''
}
viewRequestedBooking = (booking_id,rooms_id) => {
    console.log(booking_id)
    console.log(rooms_id)
    window.location.href = `/nhan-vien/dat-phong/?ma=${booking_id}&phong=${rooms_id}`
}