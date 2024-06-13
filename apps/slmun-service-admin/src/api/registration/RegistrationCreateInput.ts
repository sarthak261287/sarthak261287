import { EventWhereUniqueInput } from "../event/EventWhereUniqueInput";
import { UserWhereUniqueInput } from "../user/UserWhereUniqueInput";

export type RegistrationCreateInput = {
  event?: EventWhereUniqueInput | null;
  registrationDate?: Date | null;
  user?: UserWhereUniqueInput | null;
};
