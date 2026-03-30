---
name: invoice-generator
description: "Create professional invoices and receipts with automatic calculations. Use this skill when users want to generate, create, or manage invoices, receipts, or bills. Triggers: invoice, receipt, bill, billing, generate invoice, criar fatura, nota fiscal, recibo."
allowed-tools: [Read, Write, Edit, Bash, Browser]
license: MIT License
metadata:
    skill-author: Lucas Kefler Bergamaschi
---

# Invoice Generator

## Overview
This skill is designed to streamline the process of creating and managing professional invoices and receipts. It automates calculations for totals, taxes, and discounts, and provides customizable templates to ensure a consistent and professional brand image. Use this skill to generate invoices from scratch, from templates, or by extracting data from other documents. It is ideal for freelancers, small business owners, and anyone who needs to bill clients for services or products.

## Automatic Triggers

**ALWAYS activate this skill when user mentions:**
- Keywords: invoice, receipt, bill, billing, faturar, fatura, nota fiscal, recibo
- Phrases: "create an invoice", "generate a receipt", "how to bill a client", "criar uma fatura", "gerar um recibo"
- Context: Any discussion about creating or managing financial documents for transactions.

**Example user queries that trigger this skill:**
- "I need to create an invoice for a client."
- "Can you help me generate a receipt for a sale?"
- "Como eu faço para criar uma nota fiscal para um serviço?"

## When to Use This Skill
This skill is particularly useful in the following scenarios:

- **Freelancers and Consultants:** Quickly generate and send invoices for completed projects or billable hours.
- **Small Business Owners:** Standardize the invoicing process and maintain a professional image with clients.
- **Service Providers:** Create detailed invoices for services rendered, including itemized lists and hourly rates.
- **Retailers:** Generate receipts for sales, including calculations for sales tax and discounts.
- **Subscription-based Services:** Automate the creation of recurring invoices for subscribers.
- **Project-based Work:** Create invoices based on project milestones or deliverables.

## Core Capabilities

### 1. Invoice and Receipt Generation
This skill can create invoices and receipts in various formats, including Markdown, PDF, and HTML. You can specify the content, and the skill will format it into a professional-looking document.

**Example: Creating a simple invoice in Markdown**
```markdown
# Invoice

**From:**
Your Name/Company
Your Address

**To:**
Client Name
Client Address

**Invoice Number:** 12345
**Date:** 2026-02-02

| Description | Quantity | Price |
| --- | --- | --- |
| Service A | 1 | $100.00 |
| Service B | 2 | $50.00 |

**Total:** $200.00
```

### 2. Automatic Calculations
This skill can automatically calculate totals, taxes, and discounts. You provide the line items, quantities, and prices, and the skill will handle the rest.

**Example: Calculating total with tax**
- **Subtotal:** $200.00
- **Tax (10%):** $20.00
- **Total:** $220.00

### 3. Customizable Templates
Create and save your own invoice templates to ensure consistency and save time. You can define a template with your company's branding, and then reuse it for all your invoices.

**Template Example (`invoice-template.md`):**
```markdown
# Invoice

**From:**
Your Company Name
Your Company Address

**To:**
{{client_name}}
{{client_address}}

**Invoice Number:** {{invoice_number}}
**Date:** {{date}}

| Description | Quantity | Price |
| --- | --- | --- |
{{line_items}}

**Subtotal:** {{subtotal}}
**Tax ({{tax_rate}}%):** {{tax_amount}}
**Total:** {{total}}
```

### 4. Data Extraction
Extract invoice data from other documents, such as emails or spreadsheets. This is useful for automating the invoice creation process when you receive billing information in an unstructured format.

**Example: Extracting data from an email**
- **Email Subject:** Invoice for Project X
- **Email Body:** "Hi, please find the details for the invoice below:
  - Client: John Doe
  - Service: Web Design
  - Amount: $1500"

The skill can parse this email and create a structured invoice from it.

## Step-by-Step Workflow

1.  **Gather Invoice Information:**
    - Your company's name, address, and contact information.
    - The client's name, address, and contact information.
    - A unique invoice number.
    - The date of issue and the due date.
    - An itemized list of products or services, including descriptions, quantities, and prices.
    - Any applicable taxes or discounts.

2.  **Choose a Method for Invoice Creation:**
    - **From Scratch:** Provide all the information, and the skill will generate a new invoice.
    - **From a Template:** Use a pre-defined template to ensure consistency.
    - **From Data Extraction:** Extract information from an existing document.

3.  **Generate the Invoice:**
    - The skill will create the invoice in the specified format (e.g., Markdown, PDF, HTML).
    - It will perform all necessary calculations.

4.  **Review and Send the Invoice:**
    - Review the generated invoice for accuracy.
    - Send the invoice to the client via email or another method.

## Best Practices

- **Be Clear and Concise:** Use simple language and a clean layout. The invoice should be easy to understand at a glance.
- **Include All Necessary Information:** Make sure to include all the essential details, such as invoice number, dates, and contact information.
- **Itemize Everything:** Provide a detailed breakdown of all products and services. This helps the client understand what they are paying for.
- **State Payment Terms Clearly:** Specify the due date and the accepted payment methods.
- **Keep it Professional:** Use a professional tone and a clean design. Your invoice is a reflection of your brand.
- **Automate as Much as Possible:** Use templates and data extraction to save time and reduce errors.
- **Follow Up:** If an invoice is past due, send a polite reminder to the client.

## Examples

### Example 1: Creating a Simple Invoice for a Freelancer

**Goal:** Create an invoice for 10 hours of consulting services at $50/hour.

**Steps:**
1.  Provide the freelancer's and client's information.
2.  Add a line item for "Consulting Services" with a quantity of 10 and a price of $50.
3.  The skill will calculate the total: 10 * $50 = $500.
4.  Generate the invoice as a PDF.

### Example 2: Creating an Invoice with Tax and a Discount

**Goal:** Create an invoice for two products, with a 10% tax and a $20 discount.

**Products:**
- Product A: $100
- Product B: $150

**Steps:**
1.  Add line items for Product A and Product B.
2.  The skill calculates the subtotal: $100 + $150 = $250.
3.  The skill applies the discount: $250 - $20 = $230.
4.  The skill calculates the tax: $230 * 0.10 = $23.
5.  The skill calculates the final total: $230 + $23 = $253.
6.  Generate the invoice in HTML format.

### Example 3: Using a Template to Create an Invoice

**Goal:** Use a saved template to quickly create an invoice for a recurring client.

**Steps:**
1.  Specify the template to use (`monthly-retainer-template.md`).
2.  Provide the client's name and the current date.
3.  The skill will populate the template with the correct information and generate the invoice.

## Templates for Immediate Use

### Simple Service Invoice Template

```markdown
--- 
name: "Simple Service Invoice"
description: "A basic invoice for service-based businesses."
--- 

# Invoice

**From:**
[Your Name/Company Name]
[Your Street Address]
[Your City, State, Zip Code]
[Your Email]
[Your Phone Number]

**To:**
[Client Name]
[Client Street Address]
[Client City, State, Zip Code]

**Invoice Number:** [Invoice Number]
**Date of Issue:** [Date]
**Due Date:** [Date]

| Service Description | Hours | Rate | Amount |
| --- | --- | --- | --- |
| [Service 1] | [Hours] | [Rate] | [Amount] |
| [Service 2] | [Hours] | [Rate] | [Amount] |

**Subtotal:** [Subtotal]
**Tax ([Tax Rate]%):** [Tax Amount]
**Total:** [Total]

**Payment Instructions:**
Please make payment to [Your Bank Account Details or Payment Link].
Thank you for your business!
```

### Product Sales Invoice Template

```markdown
--- 
name: "Product Sales Invoice"
description: "A standard invoice for businesses selling products."
--- 

# Invoice

**From:**
[Your Company Name]
[Your Street Address]
[Your City, State, Zip Code]
[Your Website]
[Your Phone Number]

**Bill To:**
[Client Company Name]
[Client Contact Name]
[Client Street Address]
[Client City, State, Zip Code]

**Invoice #:** [Invoice Number]
**Date:** [Date]

| Item | Description | Quantity | Unit Price | Total |
| --- | --- | --- | --- | --- |
| [Item 1] | [Description of Item 1] | [Quantity] | [Unit Price] | [Total] |
| [Item 2] | [Description of Item 2] | [Quantity] | [Unit Price] | [Total] |

**Subtotal:** [Subtotal]
**Discount ([Discount Percentage]%):** -[Discount Amount]
**Sales Tax ([Tax Rate]%):** [Tax Amount]
**Shipping & Handling:** [Shipping Cost]
**TOTAL:** [Grand Total]

**Notes:**
[Add any additional notes or terms of service here.]
```

## References

- [Stripe: Invoice requirements: What to include and best practices](https://stripe.com/resources/more/invoice-requirements)
- [Canva: Free Online Invoice Generator](https://www.canva.com/invoice/)
- [Zoho: Free invoice maker for small businesses](https://www.zoho.com/us/invoice/)
- [QuickBooks: Free invoice generator powered by AI](https://quickbooks.intuit.com/payments/invoicing/generator/)
