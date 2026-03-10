## Skill Development Suite
A **Modular set of Odoo 16 Applications** built to support personal growth, goal setting, experiential learning through volunteering, and light collaboration.

Originally developed for the IEEE Student Branch at Al-Neelain University, this suite is ideal for volunteer-driven, non-profit, educational, and HR environments. It is also adaptable for corporate upskilling initiatives.


## Use Case Overview
This Suite was designed to support self-driven skill growth in student-led and volunteer-based environments. It allows learners to:
* Create personal skill learning plans and track growth.
* Turn the plans into focused, SMART goals.
* Break goals into structured, achievable tasks.
* Apply skills through real-world volunteering.
* Access skill-specific learning resources curated by the organization.
While it was tailored for academic volunteerism, the suite is fully adaptable to corporate HR teams, NGOs, and any organization that prioritizes talent development and continuous learning.


## Modules

| Module | Description | Status |
|---|---|---|
| [`skill_development`](skill_development/README.md) | Core learning plans module. Operates as a standalone personal tool or integrates into a corporate environment | ✅ Available |
| `resource_library` | Curated multimedia URL resource repository mapped to specific skills | 🔜 Planned |
| `volunteer_events` | Connects learners with volunteering opportunities aligned with their skills, for practical experience | 🔜 Planned |

## How To Use This Suite
* Use [`skill_development`](skill_development/README.md) alone to create and manage personal skill learning paths.
* Add `resource_library` to offer curated resources for deeper skill development (planned).
* Add `volunteer_events` to help learners apply these skills for real world settings (planned).

---
## Requirements

- Odoo 16.0
- Python 3.10+
- Odoo core modules: `base`, `hr`

## Installation

> **Important:** Install `skill_development` before installing any other module in this suite.

1. Clone the repository into your Odoo `custom_addons` directory:
   ```bash
   git clone https://github.com/FatimaMir-odoo-dev/skill-development-suite
   ```
2. Restart the Odoo server
3. Activate Developer Mode
4. Navigate to **Apps**, search for **Skill Development**, and install it
5. Optionally install additional modules from the suite as they become available

`skill_development` works out of the box with no additional configuration required. See individual module READMEs for detailed
configuration and usage instructions.

---
## Documentation

Each module contains its own `README.md` with detailed feature descriptions, 
workflow examples, and configuration instructions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

This project is licensed under [LGPL-3.0](LICENSE).
By contributing, you agree that your contributions will be licensed under the same terms.
