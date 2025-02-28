feed_xpath = '//div[@role="feed"]/div'
comment_button_xpath = '[aria-label="Viết bình luận"]'
text_box_xpath = '//div[@role="textbox"]'
send_comment_button_xpath = '//div[@role="button" and @aria-label="Bình luận"]'
close_button_xpath = '//div[@role="button" and @aria-label="Đóng"]'

share_button_xpath = '[aria-label="Gửi nội dung này cho bạn bè hoặc đăng lên trang cá nhân của bạn."]'
copy_link_button_xpath = "//span[contains(text(), 'Sao chép liên kết')]"

list_item_xpath = "//div[@role='listitem']"

message_button_xpath = "//div[@role='button' and .//span[text()='Nhắn tin']]"
message_text_box_xpath = "//*[@role='textbox' and (@aria-label='Tin nhắn' or @aria-label='Nhắn tin')]"

trust_device_button_xpath = '//span[text()="Tin cậy thiết bị này"]'
your_profile_button_xpath = "//*[@aria-label='Trang cá nhân của bạn']"
logout_button_xpath = "//span[text()='Đăng xuất']"
