DEFAULT_TO = ["ltsertwalishan@gmail.com"]
DEFAULT_CC = ["ltsertwalishan@gmail.com"]

OBSERVATION_EMAILS = {
    # "鳥音辨識": {
    #     "to": ["janiceli0918@gmail.com"],
    #     "cc": ["mntuanmu@gate.sinica.edu.tw", "jaredswu@gmail.com"],
    # },
    # "聲音指數": {
    #     "to": ["janiceli0918@gmail.com"],
    #     "cc": ["mntuanmu@gate.sinica.edu.tw", "jaredswu@gmail.com"],
    # },
    # "氣象觀測": {
    #     "to": ["jaredswu@gmail.com"],
    #     "cc": ["acropora.chen@gmail.com"],
    # },
    # "植物物候": {
    #     "to": ["900630aaa@gmail.com"],
    #     "cc": ["iling.lai@gmail.com", "jaredswu@gmail.com"],
    # },
    # "自動相機動物監測": {
    #     "to": ["sam0918075@gmail.com"],
    #     "cc": ["gjw@mail.npust.edu.tw", "jaredswu@gmail.com"],
    # },
}


def get_email_targets(observation_item):
    """
    回傳 (to_list, cc_list, bcc_list)
    - observation_item 若找不到，回退到 DEFAULT_*
    - 支援 OBSERVATION_EMAILS 裡面只填 to/cc/bcc 任一項
    """
    cfg = OBSERVATION_EMAILS.get(observation_item or "", {})
    to = cfg.get("to") or DEFAULT_TO
    cc = cfg.get("cc") or DEFAULT_CC

    if isinstance(to, str):
        to = [to]
    if isinstance(cc, str):
        cc = [cc]

    return to, cc
