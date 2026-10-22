<?php

/**
 * Installer script: generates the shared secret on first install, so the
 * plugin settings show one right away.
 *
 * @license GPL-2.0-or-later
 */

defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Installer\InstallerAdapter;
use Joomla\Registry\Registry;

class plgSystemParcellaconnectorInstallerScript
{
    public function postflight(string $type, InstallerAdapter $adapter): bool
    {
        if (!in_array($type, ['install', 'discover_install', 'update'], true)) {
            return true;
        }
        $db = Factory::getContainer()->get('DatabaseDriver');
        $query = $db->getQuery(true)
            ->select($db->quoteName(['extension_id', 'params']))
            ->from($db->quoteName('#__extensions'))
            ->where($db->quoteName('type') . ' = ' . $db->quote('plugin'))
            ->where($db->quoteName('folder') . ' = ' . $db->quote('system'))
            ->where($db->quoteName('element') . ' = ' . $db->quote('parcellaconnector'));
        $row = $db->setQuery($query)->loadObject();
        if (!$row) {
            return true;
        }
        $params = new Registry($row->params ?: '{}');
        if (strlen((string) $params->get('secret', '')) < 32) {
            $params->set('secret', bin2hex(random_bytes(32)));
            $update = $db->getQuery(true)
                ->update($db->quoteName('#__extensions'))
                ->set($db->quoteName('params') . ' = ' . $db->quote($params->toString()))
                ->where($db->quoteName('extension_id') . ' = ' . (int) $row->extension_id);
            $db->setQuery($update)->execute();
        }

        return true;
    }
}
