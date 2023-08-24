import { AuthModel } from './auth.model'

export type UserStatus = 'PAID' | 'FREE_TRIAL'

export class UserModel extends AuthModel {
  email: string
  firstname: string
  lastname: string
  plan: UserStatus
  password: string

  /*id: number
  username: string
  password: string
  fullname: string
  email: string
  pic: string
  roles: number[] = []
  occupation: string
  companyName: string
  phone: string
  address?: AddressModel
  socialNetworks?: SocialNetworksModel
  plan: UserStatus
  // personal information
  firstname: string
  lastname: string
  website: string
  // account information
  language: string
  timeZone: string
  communication: {
    email: boolean
    sms: boolean
    phone: boolean
  }
  // email settings
  emailSettings?: {
    emailNotification: boolean
    sendCopyToPersonalEmail: boolean
    activityRelatesEmail: {
      youHaveNewNotifications: boolean
      youAreSentADirectMessage: boolean
      someoneAddsYouAsAsAConnection: boolean
      uponNewOrder: boolean
      newMembershipApproval: boolean
      memberRegistration: boolean
    }
    updatesFromKeenthemes: {
      newsAboutKeenthemesProductsAndFeatureUpdates: boolean
      tipsOnGettingMoreOutOfKeen: boolean
      thingsYouMissedSindeYouLastLoggedIntoKeen: boolean
      newsAboutMetronicOnPartnerProductsAndOtherServices: boolean
      tipsOnMetronicBusinessProducts: boolean
    }
  }*/

  get isPaid(): boolean {
    return this.plan === 'PAID'
  }

  setUser(_user: unknown) {
    const user = _user as UserModel
    this.email = user.email
    this.firstname = user.firstname
    this.lastname = user.lastname
    this.plan = user.plan
    this.password = user.password
    /*this.id = user.id
    this.username = user.username || ''
    this.password = user.password || ''
    this.fullname = user.fullname || ''
    this.email = user.email || ''
    this.pic = user.pic || './assets/media/avatars/blank.png'
    this.roles = user.roles || []
    this.occupation = user.occupation || ''
    this.companyName = user.companyName || ''
    this.phone = user.phone || ''
    this.address = user.address
    this.socialNetworks = user.socialNetworks*/
  }
}
