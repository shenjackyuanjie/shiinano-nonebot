from nonebot import on_command, on_notice
from nonebot.adapters.onebot.v11 import Event, Message, MessageSegment, PokeNotifyEvent
from nonebot.params import CommandArg
from nonebot.rule import Rule, to_me
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
import math
import numpy as np
import pandas as pd

from scipy.optimize import minimize


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata

        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


calcu_dv_trigger = on_command(
    "锘 计算dv",
    aliases={"锘 jsdv", "锘jsdv", "锘计算dv", "锘 计算DV", "锘 JSDV", "锘 jsdv"},
    priority=10,
    block=True,
)
calcu_dwr_trigger = on_command(
    "锘 计算干质比", aliases={"锘 计算dwr", "锘计算干质比"}, priority=10, block=True
)
calcu_kyl_trigger = on_command("锘 康永来公式", priority=10, block=True)
calcu_gsd_trigger = on_command(
    "锘 光学卫星简单计算器", aliases={"锘 光简算", "锘光简算"}, priority=10, block=True
)
calcu_kang_opt_trigger = on_command(
    "锘 康式光学", aliases={"锘康式光学"}, priority=10, block=True
)


@calcu_dv_trigger.handle()
def calcu_dv_function(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("dv_arg", args)


@calcu_dv_trigger.got(
    "dv_arg",
    prompt="""请输入dv计算参数
格式为  “A [比冲] [全重] [油重]”
或      “B [比冲] [全重] [干重]”
单位：比冲(s) 全重(kg) 干重(kg) 油重(kg)
现已改用阿克莱(广义齐奥尔科夫斯基)公式""",
)
async def got_calcu_dv_function(dv_arg: str = ArgPlainText()):
    dv_arg_list = dv_arg.split(" ")
    if dv_arg_list[0] not in ["A", "B", "a", "b"]:
        await calcu_dv_trigger.finish(
            "你在乱输什么参数！不干了！\ntips:参数1错误，只能为A或B。"
        )
    if len(dv_arg_list) < 4:
        await calcu_dv_trigger.finish("你输入的参数不足，无法计算dv")

    if not is_number(dv_arg_list[1]):
        await calcu_dv_trigger.finish(
            "你在乱输什么参数！不干了！\ntips:比冲参数只能为数字"
        )
    if float(dv_arg_list[1]) == 0:
        await calcu_dv_trigger.finish(
            "你这发动机根本喷不出任何东西！\ntips:发动机比冲必须大于0"
        )
    if float(dv_arg_list[1]) < 0:
        await calcu_dv_trigger.finish(
            "你这发动机怎么会吸气的！\ntips:发动机比冲必须大于0"
        )

    if (not is_number(dv_arg_list[2])) or (not is_number(dv_arg_list[3])):
        await calcu_dv_trigger.finish(
            "你在乱输什么参数！不干了！\ntips:参数2或3或4错误，只能为数字"
        )

    if (float(dv_arg_list[2]) < 0) or (float(dv_arg_list[3]) < 0):
        await calcu_dv_trigger.finish(
            "如果负质量能稳定在宏观条件存在，还需要什么化学火箭！不干了！\ntips:所有参数不能为负"
        )

    if float(dv_arg_list[2]) <= float(dv_arg_list[3]):
        await calcu_dv_trigger.finish(
            "燃料质量怎么可能比总质量还多呢！不干了！\ntips:油重或干重不能大于等于总质量"
        )

    if dv_arg_list[0] in ["A", "a"]:
        c_light = float(299792458)

        isp = float(dv_arg_list[1])
        m_full = float(dv_arg_list[2])
        m_fule = float(dv_arg_list[3])

        # dv = isp*9.81*np.log(m_full/(m_full-m_fule))

        ackeret_dv_up = 1 - math.pow(
            (m_full / (m_full - m_fule)), (2 * isp * 9.81 / c_light)
        )
        ackeret_dv_down = 1 + math.pow(
            (m_full / (m_full - m_fule)), (2 * isp * 9.81 / c_light)
        )
        ackeret_dv = -c_light * ackeret_dv_up / ackeret_dv_down
        await calcu_dv_trigger.finish(
            f"计算结果：\n干质比：{round(m_full/(m_full-m_fule),3)}\nΔv={round(ackeret_dv,3)}m/s"
        )  # \n使用阿克莱公式：Δv={round(ackeret_dv,3)}m/s")

    if dv_arg_list[0] in ["B", "b"]:
        c_light = float(299792458)
        isp = float(dv_arg_list[1])
        m_full = float(dv_arg_list[2])
        m_dry = float(dv_arg_list[3])

        # dv = isp*9.81*np.log(m_full/m_dry)
        ackeret_dv_up = 1 - math.pow((m_full / m_dry), (2 * isp * 9.81 / c_light))
        ackeret_dv_down = 1 + math.pow((m_full / m_dry), (2 * isp * 9.81 / c_light))
        ackeret_dv = -c_light * ackeret_dv_up / ackeret_dv_down
        await calcu_dv_trigger.finish(
            f"计算结果：\n干质比：{round(m_full/m_dry,3)}\nΔv={round(ackeret_dv,3)}m/s"
        )
    await calcu_dv_trigger.finish("出现了其他错误！私密马楼")


@calcu_dwr_trigger.handle()
def calcu_dwr_function(matcher1: Matcher, args1: Message = CommandArg()):
    if args1.extract_plain_text():
        matcher1.set_arg("dwr_arg", args1)


@calcu_dwr_trigger.got(
    "dwr_arg",
    prompt="""请输入干质比计算参数
格式为  “[比冲] [目标Δv]”""",
)
async def got_calcu_dwr_function(dwr_arg: str = ArgPlainText()):
    dwr_arg_list = dwr_arg.split(" ")
    if len(dwr_arg_list) < 2:
        await calcu_dwr_trigger.finish("你输入的参数不足，无法计算干质比！")

    if not (is_number(dwr_arg_list[0]) or is_number(dwr_arg_list[1])):
        await calcu_dwr_trigger.finish(
            "你在乱输什么参数！不干了！\ntips:参数1或2错误，只能为数字"
        )
    isp = float(dwr_arg_list[0])
    dv = float(dwr_arg_list[1])

    c_light = float(299792458)
    upper = 1 + dv / c_light
    down = 1 - dv / c_light
    m1 = math.pow((upper / down), (c_light / (2 * isp * 9.81)))
    await calcu_dv_trigger.finish(f"干质比计算结果为：\n1：{round(m1,3)}")


calcu_hohm_trigger = on_command(
    "锘 霍曼转移",
    aliases={"锘 hohmann", "锘霍曼转移", "锘hmzy"},
    priority=10,
    block=True,
)


@calcu_hohm_trigger.handle()
def calcu_dwr_function(matcher1: Matcher, args1: Message = CommandArg()):
    if args1.extract_plain_text():
        matcher1.set_arg("hohmann_arg", args1)


@calcu_hohm_trigger.got(
    "hohmann_arg",
    prompt="""请输入霍曼转移计算参数
格式为  “[初始轨道高度] [目标轨道高度]”单位千米
目前仅支持地球霍曼转移轨道计算""",
)
async def got_calcu_hohm_function(hohmann_arg: str = ArgPlainText()):
    hohmann_arg_list = hohmann_arg.split(" ")
    mu_earth = 398600.44e9
    r_earth: float = 6378.14 * 1000  # km
    r1 = float(hohmann_arg_list[0]) * 1000 + r_earth
    r2 = float(hohmann_arg_list[1]) * 1000 + r_earth

    dv1 = math.sqrt(mu_earth / r1) * (math.sqrt(2 * r2 / (r1 + r2)) - 1)
    dv2 = math.sqrt(mu_earth / r2) * (1 - math.sqrt(2 * r1 / (r1 + r2)))
    dt = math.pi * math.sqrt(math.pow(r1 + r2, 3) / (8 * mu_earth))
    await calcu_dv_trigger.finish(f"""从{hohmann_arg_list[0]}km圆轨道转移到{hohmann_arg_list[1]}km圆轨道所需的Δv为:
第一次点火:{round(dv1,2)}m/s,
第二次点火:{round(dv2,2)}m/s
总计Δv：{round(dv1+dv2,2)}m/s
耗时：{round(dt/60,2)}分钟
计算纯属理想状态，请不要使用该结果用于星际旅行哦！""")


@calcu_kyl_trigger.handle()
async def calcu_kyl_function(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("kyl_arg", args)


@calcu_kyl_trigger.got(
    "kyl_arg", prompt="请输入康永来公式所需参数：[发动机数量] [发动机推力]"
)
async def got_kyl_function(kyl_arg: str = ArgPlainText()):
    kyl_arg_list = kyl_arg.split(" ")
    eng_num = float(kyl_arg_list[0])
    eng_thr = float(kyl_arg_list[1])
    康永来常数 = 0.015
    await calcu_kyl_trigger.finish(f"您的康箭运力为：{eng_num*eng_thr*康永来常数}t")  #


# ------------------------------------------------------------------------------


def calculate_nadir_swath(
    diameter_m, satellite_altitude_km, kang_constant, earth_radius_km=6378
):
    """
    计算0度侧摆下的星下幅宽，基于卫星的口径、轨道高度和康常数（调节系数）。

    参数:
    - diameter_m (float): 光学系统的口径（单位：米）
    - satellite_altitude_km (float): 卫星的轨道高度（单位：千米）
    - kang_constant (float): 康常数（调节系数），用于计算焦距
    - earth_radius_km (float): 地球半径（单位：千米），默认值为6378千米

    返回:
    - float: 0度侧摆的星下幅宽（单位：千米）
    """
    # 计算焦距，使用康常数作为调节系数
    focal_length_m = kang_constant * diameter_m

    # 计算视场角（FOV）
    half_fov_rad = np.arctan((diameter_m / 2) / focal_length_m)

    # 计算0度侧摆下的星下幅宽
    satellite_altitude_m = satellite_altitude_km * 1000
    nadir_swath_m = 2 * satellite_altitude_m * np.tan(half_fov_rad)

    # 将结果转换为千米
    nadir_swath_km = nadir_swath_m / 1000
    return nadir_swath_km


def kang_swath_width_adjusted(
    off_nadir_angle_deg, nadir_swath_width_km, a=25.14, b=3.30
):
    """
    计算侧摆角度下的卫星幅宽，基于“康式幅宽法”，并根据给定的0度星下幅宽进行动态调整。

    参数:
    - off_nadir_angle_deg (float): 侧摆角度（单位：度）
    - nadir_swath_width_km (float): 0度星下幅宽的基础值（单位：千米）
    - a (float): 康式幅宽法中的参数
    - b (float): 康式幅宽法中的参数

    返回:
    - float: 幅宽（单位：千米）
    """
    # 计算调整项 c，使得在0度侧摆时，幅宽等于计算的0度星下幅宽
    c = nadir_swath_width_km - (a * (np.tan(np.radians(0)) ** b))

    # 根据侧摆角度计算幅宽
    swath_width_km = a * (np.tan(np.radians(off_nadir_angle_deg)) ** b) + c
    return swath_width_km


# 使用示例
diameter = 1.5  # 光学口径（米）
altitude_km = 700  # 轨道高度（千米）
kang_constant = 36.84  # 康常数


# ------------------------------------------------------------------------------


# Comprehensive sensor calculation considering Earth curvature, GSD, and GRD for multiple bands
def comprehensive_sensor_calculations(
    altitude,
    aperture,
    f_number,
    pixel_size,
    off_nadir_angle,
    wavelength_dict,
    earth_radius=6378000,
):
    """
    计算地面分辨率(GSD)、各波段衍射极限分辨率(GRD)、全口径潜力幅宽和近接幅宽。

    参数:
    - altitude: 轨道高度，单位米
    - aperture: 光学系统口径，单位米
    - f_number: F数 (焦距 = F数 * 口径)
    - pixel_size: 探测器像元尺寸，单位米
    - off_nadir_angle: 与地面垂直方向的侧摆角度，单位度
    - wavelength_dict: 各波段的波长字典，单位米
    - earth_radius: 地球半径，默认为6378000米

    返回:
    - DataFrame: 包含GSD、各波段GRD、全口径潜力幅宽和近接幅宽的表格。
    """

    # 根据F数和口径计算焦距
    focal_length = f_number * aperture

    # 计算地面分辨率 (GSD)，考虑侧摆角度
    def calculate_gsd(altitude, pixel_size, focal_length, off_nadir_angle):
        # GSD = (高度 * 像元尺寸 / 焦距) / cos(侧摆角)
        return (altitude * pixel_size / focal_length) / np.cos(
            np.radians(off_nadir_angle)
        )

    # 计算衍射极限分辨率 (GRD) for each spectral band
    def calculate_grd(altitude, aperture, wavelength):
        # GRD = 1.22 * 波长 * 高度 / 口径
        return 1.22 * wavelength * altitude / aperture

    # 计算幅宽，包含地球曲率和侧摆角度
    def calculate_swath_with_curvature(
        altitude, field_of_view, off_nadir_angle=0, earth_radius=6378000
    ):
        # 有效高度计算，包含地球曲率
        effective_altitude = earth_radius * (
            np.sqrt(1 + 2 * altitude / earth_radius) - 1
        )
        # 幅宽计算公式：2 * 有效高度 * tan((视场角 + 侧摆角) / 2)
        return (
            2
            * effective_altitude
            * np.tan((field_of_view + np.radians(off_nadir_angle)) / 2)
        )

    # 计算全口径潜力幅宽
    def calculate_potential_swath(altitude, aperture, focal_length):
        # 宽度为光学系统口径的对角线
        width = aperture / np.sqrt(2)
        # 视场角计算
        field_of_view = 2 * np.arctan(width / (2 * focal_length))
        return calculate_swath_with_curvature(altitude, field_of_view, off_nadir_angle)

    # 计算近接幅宽，假设探测器宽度为口径的36%
    def calculate_near_contact_swath(altitude, aperture, focal_length, ratio=0.36):
        width = ratio * (aperture / np.sqrt(2))
        field_of_view = 2 * np.arctan(width / (2 * focal_length))
        return calculate_swath_with_curvature(altitude, field_of_view, off_nadir_angle)

    # 执行计算
    gsd = calculate_gsd(altitude, pixel_size, focal_length, off_nadir_angle)

    grd_data = {}
    for band, wavelength in wavelength_dict.items():
        grd_data[band] = calculate_grd(altitude, aperture, wavelength)

    potential_swath = calculate_potential_swath(altitude, aperture, focal_length)
    near_contact_swath = calculate_near_contact_swath(altitude, aperture, focal_length)

    # 将所有数据组织成 DataFrame
    results = {
        "Parameter": ["GSD (m)", "Potential Swath (km)", "Near Contact Swath (km)"]
        + [f"GRD - {band} (m)" for band in wavelength_dict],
        "Value": [gsd, potential_swath / 1000, near_contact_swath / 1000]
        + list(grd_data.values()),
    }

    df_results = pd.DataFrame(results)

    text_result = f""" 计算结果默认NOFORN/REL SETI
===光学卫星简单计算器===
地面采样分辨率:{gsd/1000000:.3f}m
全口径潜力宽幅：{potential_swath/1000:.3f}km
近接宽幅:{near_contact_swath/1000:.3f}km
衍射极限分辨率(GRD)分辨率计算结果：
可见光:{grd_data['Visible']:.3f}m
近红外:{grd_data['NIR']:.3f}m
短波红外SWIR:{grd_data['SWIR']:.3f}m
中波红外MWIR:{grd_data['MWIR']:.3f}m
长波红外LWIR:{grd_data['LWIR']:.3f}m
红外直达地面SWSTG:{grd_data['SWSTG']:.3f}m
远红外FIR:{grd_data['FIR']:.3f}m
"""
    return [text_result, near_contact_swath]


# 示例参数
altitude = 400000  # 轨道高度，单位米
aperture = 3.5  # 光学系统口径，单位米
f_number = 10  # F数
pixel_size = 3e-6  # 像元尺寸，单位米
off_nadir_angle = 20  # 侧摆角，单位度

# 各波段的波长，单位米
wavelength_dict = {
    "Visible": 0.55e-6,
    "NIR": 0.85e-6,
    "SWIR": 1.5e-6,
    "MWIR": 4.0e-6,
    "LWIR": 10.0e-6,
    "SWSTG": 1.6e-6,
    "FIR": 12.0e-6,
}

# 运行综合传感器计算
df_results = comprehensive_sensor_calculations(
    altitude, aperture, f_number, pixel_size, off_nadir_angle, wavelength_dict
)

# 打印结果
print(df_results)


# ------------------------------------------------------------------------------


@calcu_gsd_trigger.handle()
async def calcu_gsd_function(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("gsd_arg", args)


@calcu_gsd_trigger.got(
    "gsd_arg",
    prompt="""===光学卫星简单计算器===
请输入计算所需的参数
格式：“[卫星高度] [口径] [f数] [像元尺寸] [侧摆角]”
单位：[km] [m] [/] [μm] [°]""",
)
async def got_gsd_function(event: Event, gsd_arg: str = ArgPlainText()):
    list_gsd_arg = gsd_arg.split(" ")
    m高度 = float(list_gsd_arg[0]) * 1000
    m口径 = float(list_gsd_arg[1])
    mf = float(list_gsd_arg[2])
    m像元尺寸 = float(list_gsd_arg[3])
    m侧摆角 = float(list_gsd_arg[4])
    # gsd_result = 综合传感器计算(m高度, m口径, m焦距, m像元尺寸, m侧摆角, 波长字典)

    gsd_result = comprehensive_sensor_calculations(
        m高度, m口径, mf, m像元尺寸, m侧摆角, wavelength_dict
    )
    print(gsd_result)

    nadir_swath_value = calculate_nadir_swath(m口径, m高度 / 1000, 36.84)

    # 第二步：根据实际侧摆角度要求计算幅宽

    off_nadir_angle = m侧摆角  # 例如，计算30度侧摆角度下的幅宽
    calculated_swath_width = kang_swath_width_adjusted(m侧摆角, gsd_result[1])

    await calcu_dv_trigger.finish(
        MessageSegment.at(event.get_user_id())
        + MessageSegment.text(gsd_result[0])
        + MessageSegment.text(
            f"---使用康式拟合法---\n0度星下幅宽: {nadir_swath_value:.3f} km\n{off_nadir_angle}度侧摆角度下的幅宽: {calculated_swath_width:.3f} km"
        )
    )


@calcu_kang_opt_trigger.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("kangopt_arg", args)


@calcu_kang_opt_trigger.got(
    "kangopt_arg",
    prompt="""===康氏光学卫星简单计算器===
请输入计算所需的参数
格式：“[光学系统口径(m)] [轨道高度(km)] [康永来光学常数] [侧摆角度] [0度基础值]”""",
)
async def _(event: Event, kangopt_arg: str = ArgPlainText()):
    list_kangopt_arg = kangopt_arg.split(" ")
    M_diameter = float(list_kangopt_arg[0])
    M_altitude_km = float(list_kangopt_arg[1])
    M_kang_constant = float(list_kangopt_arg[2])
    M_off_nadir_angle = float(list_kangopt_arg[3])
    M_nadir_swath_value = float(list_kangopt_arg[4])
    # 第一步：计算0度侧摆下的星下幅宽
    nadir_swath_value = calculate_nadir_swath(
        M_diameter, M_altitude_km, M_kang_constant
    )

    # 第二步：根据实际侧摆角度要求计算幅宽
    off_nadir_angle = 30  # 例如，计算30度侧摆角度下的幅宽
    calculated_swath_width = kang_swath_width_adjusted(
        M_off_nadir_angle, M_nadir_swath_value
    )

    # 输出结果
    await calcu_kang_opt_trigger.finish(
        f"0度星下幅宽: {nadir_swath_value} km\n{off_nadir_angle}度侧摆角度下的幅宽: {calculated_swath_width} km"
    )
