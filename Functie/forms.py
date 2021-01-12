# -*- coding: utf-8 -*-

#  Copyright (c) 2020-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django import forms


class OTPControleForm(forms.Form):
    """ Dit formulier wordt gebruikt om de OTP code te ontvangen van de gebruiker """

    otp_code = forms.CharField(
                        label='Code',
                        min_length=6,
                        max_length=6,
                        required=True,
                        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'off'}))

    def is_valid(self):
        valid = super(forms.Form, self).is_valid()
        if valid:
            otp_code = self.cleaned_data.get('otp_code')
            try:
                code = int(otp_code)
            except ValueError:
                self.add_error(None, 'Voer de vereiste code in')
                valid = False
        else:
            self.add_error(None, 'De gegevens worden niet geaccepteerd')

        return valid


# end of file
