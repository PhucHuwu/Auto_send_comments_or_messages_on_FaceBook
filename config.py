feed_xpath = '//div[@role="feed"]/div'

comment_button_xpath = '[aria-label="Viết bình luận"]'
comment_button_xpath_eng = '[aria-label="Leave a comment"]'  # -----

text_box_xpath = '//div[@role="textbox"]'

share_button_xpath = '[aria-label="Gửi nội dung này cho bạn bè hoặc đăng lên trang cá nhân của bạn."]'
share_button_xpath_eng = '[aria-label="Send this to friends or post it on your profile."]'  # -----

copy_link_button_xpath = "//span[contains(text(), 'Sao chép liên kết')]"
copy_link_button_xpath_eng = "//span[contains(text(), 'Copy link')]"  # -----

list_item_xpath = "//div[@role='listitem']"

message_button_xpath = "//div[@role='button' and .//span[text()='Nhắn tin']]"
message_button_xpath_eng = "//div[@role='button' and .//span[text()='Message']]"  # -----

message_text_box_xpath = "//*[@role='textbox' and (@aria-label='Tin nhắn' or @aria-label='Nhắn tin')]"

try_another_way_button_xpath = "//*[contains(text(), 'Thử cách khác')]"
try_another_way_button_xpath_eng = "//*[contains(text(), 'Try Another Way')]"

authentication_button_xpath = "//*[contains(text(), 'Ứng dụng xác thực')]"
authentication_button_xpath_eng = "//*[contains(text(), 'Authentication app')]"

auth_check_box_xpath = "./ancestor::div[1]//following::input[@type='radio'][1]"

continue_button_xpath = "//span[contains(text(), 'Tiếp tục')]"
continue_button_xpath_eng = "//span[contains(text(), 'Continue')]"

trust_device_button_xpath = '//span[text()="Tin cậy thiết bị này"]'
trust_device_button_xpath_eng = '//span[text()="Trust this device"]'

your_profile_button_xpath = "//*[@aria-label='Trang cá nhân của bạn']"
your_profile_button_xpath_eng = "//*[@aria-label='Your profile']"  # -----

checkpoint_account_logout_button_xpath = "div[aria-label='Lựa chọn khác']"
checkpoint_account_logout_button_xpath_eng = "div[aria-label='More options']"

logout_button_xpath = "//span[text()='Đăng xuất']"
logout_button_xpath_eng = "//span[text()='Log Out']"

logout_disable_180d_button_xpath = "//div[@role='button'][.//span[contains(text(),'Đăng xuất')]]"
logout_disable_180d_button_xpath_eng = "//div[@role='button'][.//span[contains(text(),'Log Out')]]"

#----------------------------------------------------------------------------------------------------------------------
write_something_text_box_xpath = "//span[text()='Bạn viết gì đi...']"
select_color_button_xpath = "//div[@aria-label='Hiển thị các tùy chọn phông nền']"
color_select_xpath = "//div[contains(@style, 'linear-gradient(45deg, rgb(255, 0, 71), rgb(44, 52, 199))')]"
post_button_xpath = "//span[text()='Đăng']"

filter_public_group_xpath = "//input[@aria-label='Nhóm công khai']"
