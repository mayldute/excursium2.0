import enum

class ClientTypeEnum(str, enum.Enum):
    IND = "IND" #Individual 
    LEG = "LEG" #Legal entity

class LegalTypeEnum(str, enum.Enum):
    GP = "GP" #General partnership
    LP = "LP" #Limited partnership
    EC = "EC" #Economic company
    PJC = "PJC" #Private joint-stock company
    NJC = "NJC" #Non-joint-stock company
    LLC = "LLC" #Limited liability company
    IE = "IE" #Individual entrepreneur
    UE = "UE" #Unitary Enterprise
    FD = "FD" #Fund
    EST = "EST" #Establishment
    OTH = "OTH" #Other

class DocTypeEnum(str, enum.Enum):
    LC = "LC" #Licence
    ME = "ME" #Medical examination
    IS = "IS" #Insurance
    CT = "CT" #Contract

class OrderStatusEnum(str, enum.Enum):
    NEW = "NEW"   #New
    CONFIRMD = "CONFIRMED" #Confirmed
    IN_PROGRESS = "IN_PROGRESS" #In progress
    COMPLETED = "COMPLETED" #Completed
    REJECTED = "REJECTED" #Rejected
    ARCHIVED = "ARCHIVED" #Archived

class PassenderTypeEnum(str, enum.Enum):
    CHILDREN = "CHILDREN" #Children
    ADULT = "ADULT" #Adult
    MIXED = "MIXED" #Mixed
    CORPORATE = "CORPORATE" #Corporate

class PaymentMethodEnum(str, enum.Enum):
    CARD = "CARD" #Card
    TRANSFER = "TRANSFER" #Transfer
    OTHER = "OTHER" #Apple Pay / Google Pay / SBP for individuals