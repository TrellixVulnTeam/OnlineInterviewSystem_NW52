# OnlineInterviewSystem-OIS

- OIS----中山一中2023模拟招聘会线上面试系统
- Developed By Hadream(Lanzhijiang)
- Hadream reserve all copyrights 

## Component

#### OIIS

- 线上面试信息系统

- 重在传达信息，包含了OICS-叫号系统，是为了没有摄像头而设计的 (waiting_room_client+class_client_backend)

#### OICS

- 线上面试叫号系统(叫学生从班级到电脑室面试)

- 分为：WaitingRoomClient和ClassClient

- 使用socket通讯，配合Backend

#### WebCustomerClient(OIISApplySystem)

- 线上面试C端，包括了ApplySystem和MeetingAssignSystem，分别是报名和会议室分配系统

- 在../ApplySystem中，不在此处

- 使用django框架

### 数据库设计

- 使用MongoDB非关系型数据库

- 四种用户：candidate interviewer class waiting_room

- interview数据库为存储报名信息，面试终端信息的数据库

- calling集合为存储叫号数据的集合，以做到叫号不被中断，可以及时恢复
