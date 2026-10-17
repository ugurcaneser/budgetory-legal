# Budgetory legal pages

The privacy policy and the account deletion page of Budgetory, the personal budgeting app by Uğurcan Eser, served by GitHub Pages from `docs/`:

- Privacy policy: https://ugurcaneser.github.io/budgetory-legal/
- Deleting an account: https://ugurcaneser.github.io/budgetory-legal/delete-account.html

Both pages are in English, Türkçe, Deutsch, Français, Español and Русский.

## Updating the pages

The policy's texts are the app's own (`locales/<lang>.json`, shown in this order by `components/PrivacyPolicyModal.tsx`), so the app and the web page always say the same thing. The deletion page's texts are in `deletion/<lang>.json`. After changing either, rebuild `docs/` and commit it:

```
python3 build.py    # reads the app from ../Budgetory, or from $BUDGETORY_APP
```
